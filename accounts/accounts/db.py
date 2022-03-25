import asyncio

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.app.config import settings


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def init_models(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def db_init_models():
    asyncio.run(init_models())


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        pass
