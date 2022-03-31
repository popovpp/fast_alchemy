from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel
from sqlalchemy.orm import Session

from sqlalchemy import select


# Define abstract types for SQLAlchemy model, and Pydantic schemas
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseActions(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    async def get_all(self, model, obj_ordered_attr: str, db: Session, *, skip: int = 0,
                      limit: int = 100) -> List[ModelType]:
        result = await db.execute(select(model).order_by(getattr(model, obj_ordered_attr, None)).offset(skip).limit(limit))
        return result.scalars().all()

    @classmethod
    async def get_by_attr(self, model, attr_value, attr_name: str, db: Session) -> Optional[ModelType]:
        print(db)
        result = await db.execute(select(model).filter(getattr(model, attr_name, None)==attr_value))
        return result.scalars().first()

    async def create(self, db: Session, *, db_obj: CreateSchemaType) -> ModelType:
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        await db.close()
        return db_obj

    async def update(self, db: Session, *, db_obj: ModelType, 
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
        await db.commit()
        await db.refresh(db_obj)
        await db.close()
        return db_obj

    async def remove(self, obj, *, db: Session) -> ModelType:
        await db.delete(obj)
        await db.commit()
        await db.close()
        return obj
