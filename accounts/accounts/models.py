"""
NAME
====
models - модуль, содержащий модель User

VERSION
=======
0.1.0

SYNOPSIS
========

    from accounts.models import User

DESCRIPTION
===========
Модуль содержит модель User.

MODEL
======
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy_utils import UUIDType
from passlib.context import CryptContext

from .db import Base


class User(Base):
    """Модель User"""
    
    __tablename__ = "users"
    hasher= CryptContext(schemes=['bcrypt'])

    id = Column(UUIDType(binary=False),
                primary_key=True,
                index=True,
                default=uuid4)
    email = Column(String, nullable=False)
    password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created = Column(String, nullable=False)
    last_login = Column(String, nullable=True)

    def set_password(self, password):
        """Установить пароль"""
        self.password = self.hasher.hash(password)

    def set_is_active_false(self):
        """Установить флаг is_active в False"""
        self.is_active = False

    def set_is_superuser_false(self):
        """Установить флаг is_superuser в False"""
        self.is_superuser = False

    def set_is_active_true(self):
        """Установить флаг is_active в True"""
        self.is_active = True

    def set_is_superuser_true(self):
        """Установить флаг is_superuser в True"""
        self.is_superuser = True

    def set_is_verified_false(self):
        """Установить флаг is_verified в False"""
        self.is_verified = False

    def set_is_verified_true(self):
        """Установить флаг is_verified в True"""
        self.is_verified = True

    def set_created(self):
        """Установить время создания записи"""
        self.created = str(datetime.now())

    def set_last_login(self):
        """Установить время последнего входа пользователя"""
        self.last_login = str(datetime.now())
