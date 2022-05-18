from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel
from sqlalchemy.orm import Session, Query
from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


# Определяем абстрактные типы для SQLAlchemy модели, и Pydantic схем
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseActions(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс, содержащий CRUD методы для взаимодействия с БД
    """

    async def get_all(self, model, obj_ordered_attr: str,
                      db: Session, *, skip: int = 0,
                      limit: int = 100) -> List[ModelType]:
        """
        Получить все экземпляры объекта `model`, содержащиеся в БД, по которой открыта 
        сессия `db`. Отсортировать полученные объекты по атрибуту `obj_ordered_attr` 
        """
        try:
            result = await db.execute(
                select(model).order_by(desc(getattr(model, obj_ordered_attr, None))
                ).offset(
                    skip
                ).limit(
                    limit
                )
            )
            result = result.scalars().all()
            await db.close()
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            await db.close()

    @classmethod
    async def get_by_attr_first(self, model, 
                          attr_value, 
                          attr_name: str, 
                          db: Session) -> Optional[ModelType]:
        """
        Получить первый экземпляр объекта `model` из БД `db` по атрибуту `attr_name`, 
        имеющим значение `attr_value`.
        """
        try:
            result = await db.execute(
                select(model).filter(
                    getattr(model, attr_name, None)==attr_value
                ).order_by(
                    desc(getattr(model, attr_name, None))
                )
            )
            result = result.scalars().first()
            await db.close()
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            await db.close()

    async def get_by_attr_all(self, model,
                              attr_value,
                              attr_name: str,
                              db: Session, *,
                              skip: int = 0,
                              limit: int = 100) -> Optional[ModelType]:
        """
        Получить все экземпляры объекта `model` из БД `db` с атрибутом `attr_name`, 
        имеющим значение `attr_value` отсортированные по `id`
        """
        try:
            result = await db.execute(
                select(model).filter(
                    getattr(model, attr_name, None)==attr_value
                ).order_by(
                    desc(getattr(model, 'id', None))
                ).offset(
                    skip
                ).limit(
                    limit
                )
            )
            result = result.scalars().all()
            await db.close()
            return result
        except SQLAlchemyError as e:
            raise e
        finally:
            await db.close()

    async def create(self, db: Session, *, db_obj: CreateSchemaType) -> ModelType:
        """
        Создать в БД `db` запись, хранящую объект `db_obj`
        """
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            await db.close()
            return db_obj
        except SQLAlchemyError as e:
            raise e
        finally:
            await db.close()

    async def update(self, db: Session, *, db_obj: ModelType, 
                     obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Обновить в БД `db` запись, содержащую объект `db_obj` данными, содержащимися в 
        словаре `obj_in`.
        """
        try:
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
        except SQLAlchemyError as e:
            raise e
        finally:
            await db.close()

    async def remove(self, obj, *, db: Session) -> ModelType:
        """
        Удалить запись из БД `db`, содержащую объект `obj`
        """
        try:
            await db.delete(obj)
            await db.commit()
            await db.close()
            return obj
        except SQLAlchemyError as e:
            raise e
        finally:
            await db.close()


    async def get_by_query_all(self, model,
                              query: Query,
                              db: Session, *,
                              skip: int = 0,
                              limit: int = 100) -> Optional[ModelType]:
        """
        TODO
        Получить все экземпляры объекта `model` из БД `db` по запросу `query`
        """

        pass
