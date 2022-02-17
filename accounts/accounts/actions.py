from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel
from sqlalchemy.orm import Session

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from .db import Base
from .models import User

# Define custom types for SQLAlchemy model, and Pydantic schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseActions(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """Base class that can be extend by other action classes.
           Provides basic CRUD and listing operations.

        :param model: The SQLAlchemy model
        :type model: Type[ModelType]
        """
        self.model = model

    async def get_all(self, db: Session, *, skip: int = 0,
                      limit: int = 100) -> List[ModelType]:
        result = await db.execute(select(User).order_by(User.id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get(self, db: Session, id: UUID4) -> Optional[ModelType]:
        result = await db.execute(select(User).filter(User.id==id))
        return result.scalars().first()

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        print(db, '######################################')
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        
        print(db_obj, '###################################')
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, 
               obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID4) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


class UserActions(BaseActions[User, schemas.UserCreated, schemas.UserUpdate]):
    """User actions with basic CRUD operations"""

    pass


user = UserActions(User)
