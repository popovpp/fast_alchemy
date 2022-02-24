import os
import jwt # used for encoding and decoding jwt tokens
from fastapi import HTTPException # used to handle error handling
#from passlib.context import CryptContext # used for hashing the password 
from datetime import datetime, timedelta # used to handle expiry time for tokens


class Auth():
#    hasher= CryptContext(schemes=['bcrypt'])
    secret = '11111111'#os.getenv("APP_SECRET_STRING")

    async def encode_password(self, password):
        return await self.hasher.hash(password)

    async def verify_password(self, password, encoded_password):
        return await self.hasher.verify(password, encoded_password)

    async def encode_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, minutes=30),
            'iat' : datetime.utcnow(),
            'scope': 'access_token',
            'sub' : username
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm='HS256'
        )

    async def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    async def encode_refresh_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, hours=10),
            'iat' : datetime.utcnow(),
            'scope': 'refresh_token',
            'sub' : username
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm='HS256'
        )

    async def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=['HS256'])
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = await self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')
