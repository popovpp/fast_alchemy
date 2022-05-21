"""
NAME
====
db - модуль подключения к БД

VERSION
=======
0.1.0

SYNOPSIS
========

    from accounts.db import get_db, Base

DESCRIPTION
===========
Модуль, осуществляющий асинхронное подключение к БД и содержащий генератор сессий.

MODEL
======
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.app.config import settings


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Генератор сессий подключения к БД"""
    try:
        db = SessionLocal()
        yield db
    finally:
        pass
