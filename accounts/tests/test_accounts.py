import pytest
from faker import Faker
from fastapi import Depends

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from app.app.config import settings

from app.app import __version__
#from accounts.db import get_db
from accounts.models import User
from accounts.main import user_actions


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
    return User(email=fake.ascii_email(), password='password')


@pytest.fixture
def get_user_list():
    print(fake.ascii_email())
    print(engine)
    print(settings.SQLALCHEMY_DATABASE_URI)
    return [User(email=fake.ascii_email(), password='password') for _ in range(5)]


class TestApp:
        
    def test_version(self):
        assert __version__ == '0.1.0'
    
    @pytest.mark.asyncio
    async def test_get_all(self, get_user_list, db: Session = Depends(get_db)):
        for user in get_user_list:
            print(db)
            user_actions.create(db=db, db_obj=user)
            print(user)
        print(await user_actions.get_all(User, 'created',db=get_db()))
        assert await user_actions.get_all(User, 'created',db=get_db())

    def test_get_attr(self):
        pass

    def test_create(self):
        pass

    def test_update(self):
        pass

    def test_remove(self):
        pass
