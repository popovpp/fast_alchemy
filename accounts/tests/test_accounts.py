import pytest
import asyncio
import random
from faker import Faker
from fastapi import Depends

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from app.app.config import settings

from app.app import __version__
from accounts.db import get_db, engine, SessionLocal
from accounts.models import User
from accounts.main import user_actions


fake = Faker()


@pytest.fixture
def get_user():
    user = User(email=fake.ascii_email(), password='password')
    user.set_password('password')
    user.set_is_verified_false()
    user.set_is_superuser_false()
    user.set_created()
    return user


@pytest.fixture
def get_rand_attr():
    attr_list = [
        'id',
        'email',
        'password',
        'is_active',
        'is_verified',
        'is_superuser',
        'created'
    ]
    return random.choice(attr_list)


class TestApp:
        
    def test_version(self):
        assert __version__ == '0.1.0'
    
    @pytest.mark.asyncio
    async def test_get_all(self, db=SessionLocal()):
        assert  len(await user_actions.get_all(User, 'created', db=db)) >= 0

    @pytest.mark.asyncio
    async def test_get_attr(self, get_user, get_rand_attr, db=SessionLocal()):
        attr = get_rand_attr
        user = get_user
        await user_actions.create(db=db, db_obj=user)
        user_readed = await user_actions.get_by_attr(User, getattr(user, attr), attr, db=db)
        assert getattr(user, attr) == getattr(user_readed, attr)
        await user_actions.remove(user_readed, db=db)

    @pytest.mark.asyncio
    async def test_create(self, get_user, db=SessionLocal()):
        user_created = get_user
        await user_actions.create(db=db, db_obj=user_created)
        user_readed = await user_actions.get_by_attr(User, user_created.email, 'email', db=db)
        assert user_created.id == user_readed.id
        await user_actions.remove(user_readed, db=db)

    def test_update(self):
        pass

    def test_remove(self):
        pass
