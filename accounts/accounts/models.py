import hashlib

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from fastapi import HTTPException

from .db import Base


class User(Base):
    __tablename__ = "users"
    hasher= CryptContext(schemes=['bcrypt'])

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
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
        self.password = self.hasher.hash(password)

    def verify_password(self, password):
        try:
            return self.hasher.verify(password, self.password)
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    def set_is_active_false(self):
        self.is_active = False

    def set_is_superuser_false(self):
        self.is_superuser = False

    def set_is_active_true(self):
        self.is_active = True

    def set_is_superuser_true(self):
        self.is_superuser = True

    def set_is_verified_false(self):
        self.is_verified = False

    def set_is_verified_true(self):
        self.is_verified = True

    def set_created(self):
        self.created = str(datetime.now())

    def set_last_login(self):
        self.created = str(datetime.now())
