from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@as_declarative()
class Base:
    id: Any
    