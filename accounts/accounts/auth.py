"""
NAME
====
auth - модуль, сождержащий методы необходимые для авторизации

VERSION
=======
0.1.0

SYNOPSIS
========

    from accounts.auth import Auth

    auth_handler = Auth()

DESCRIPTION
===========
Модуль, содержащий класс Auth, имеющий в своем составе методы для верификации
пароля пользователя, кодирования и декодирования access и refresh токенов.

MODEL
======
"""

import os
import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.app.config import TOKEN_EXP_TIME
from .models import User


class Auth():
    """Класс, реализующий методы верификации пароля, кодирования и декодирования jwt-токена"""
    secret = os.getenv("AUTH_SECRET_STRING")
    hasher= CryptContext(schemes=['bcrypt'])

    async def verify_password(self, password, encoded_password):
        """Верификация пароля"""
        return self.hasher.verify(password, encoded_password)

    async def encode_token(self, user):
        """Кодирование access токена"""
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, minutes=TOKEN_EXP_TIME),
            'iat' : datetime.utcnow(),
            'scope': 'access_token',
            'sub' : {
                        "username": user.email,
                        "user_id": str(user.id)
                    }
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm='HS256'
        )

    async def decode_token(self, token):
        """Декодирование access токена"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    async def encode_refresh_token(self, user):
        """Кодирование refresh токена"""
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, hours=10),
            'iat' : datetime.utcnow(),
            'scope': 'refresh_token',
            'sub' : {
                        "username": user.email,
                        "user_id": str(user.id)
                    }
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm='HS256'
        )

    async def refresh_token(self, refresh_token):
        """Декодировнаие refresh токена"""
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=['HS256'])
            if (payload['scope'] == 'refresh_token'):
                sub = payload['sub']
                user = User(id=sub['user_id'], email=sub['username'])
                new_token = await self.encode_token(user)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')
