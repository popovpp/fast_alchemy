from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
# from fastapi.security import OAuth2PasswordBearer

from . import actions, models, schemas
from .db import SessionLocal, engine
from .models import User


app = FastAPI()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency to get DB session.
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        pass
#        db.close()


@app.get("/")
def index():
    return {"message": "Hello world!"}


@app.get("/users", response_model=List[schemas.User], tags=["users"])
async def list_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    users = await actions.user.get_all(db=db, skip=skip, limit=limit)
    return users


@app.post(
    "/users", response_model=schemas.UserCreated, status_code=HTTP_201_CREATED, tags=["users"]
)
async def create_user(*, db: Session = Depends(get_db), user_in: schemas.UserCreating) -> Any:
    user_in_data = jsonable_encoder(user_in)
    user = await db.execute(select(User).filter(User.email==user_in_data['email']))
    user = user.scalars().first()
    if user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User with same email already exist")
    db_user = User(**user_in_data)  # type: ignore
    db_user.set_password(user_in_data['password'])
    db_user.set_is_active_false()
    db_user.set_is_superuser_false()
    user = await actions.user.create(db=db, db_obj=db_user)
    return {'id': user.id,
            'email': user.email}


@app.put(
    "/users/{id}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
async def update_user(*, db: Session = Depends(get_db), id: UUID4, 
                user_in: schemas.UserUpdate, ) -> Any:
    user = await actions.user.get(db=db, id=id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    user = await actions.user.update(db=db, db_obj=user, obj_in=user_in)
    return user


@app.get(
    "/users/{id}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
async def get_user(*, db: Session = Depends(get_db), id: UUID4) -> Any:
    user = await actions.user.get(db=db, id=id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.delete(
    "/users/{id}",
    response_model=schemas.HTTPNoContent,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
async def delete_user(*, db: Session = Depends(get_db), id: UUID4) -> Any:
    user = await actions.user.get(db=db, id=id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    user = await actions.user.remove(db=db, obj=user)
    return {'detail': 'No content'}


# @app.get("/items/")
# def read_items(token: str = Depends(oauth2_scheme)):
#     return {"token": token}
