import hashlib

from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID

from .db import Base


class User(Base):
    __tablename__ = "users"

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
        self.password = hashlib.md5(password.strip().encode()).hexdigest()

    def set_is_active_false(self):
        self.is_active = False

    def set_is_superuser_false(self):
        self.is_superuser = False

    def set_is_active_true(self):
        self.is_active = True

    def set_is_superuser_true(self):
        self.is_superuser = True
