import pytest
from faker import Faker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

from app import __version__
# from accounts.accounts.db import get_db
from accounts.accounts.models import User
from accounts.accounts.main import user_actions


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        pass


fake = Faker()


@pytest.fixture
def get_user():
    return User(email=fake.providers.profile.mail, password='password')


@pytest.fixture
def get_user_list():
    return [User(email=fake.providers.profile.mail, password='password') for _ in range(5)]


class TestApp:

    def test_version(self):
        assert __version__ == '0.1.0'

    def test_get_all(self, get_user_list):
        for user in get_user_list:
            user_actions.create(get_db, user)
        assert user_actions.get_all(User, 'email', get_db())

    def test_get_attr(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_remove(self):
        pass
