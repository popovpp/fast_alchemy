import passlib

from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException, Security
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import (HTTP_201_CREATED, HTTP_404_NOT_FOUND,
                              HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                              HTTP_401_UNAUTHORIZED,)

from . import actions, models, schemas
from .db import SessionLocal, engine
from .models import User
from .auth import Auth


app = FastAPI()


security = HTTPBearer()
auth_handler = Auth()


async def get_current_user(db: Session, token: str = Depends(security)):
    email = await auth_handler.decode_token(token)
    user = await actions.user.get_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


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
    return {"message": "You are wellcome!"}


@app.get("/users", response_model=List[schemas.User], tags=["users"])
async def list_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100,
                     credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    current_user = await get_current_user(db=db, token=credentials.credentials)
    users = await actions.user.get_all(db=db, skip=skip, limit=limit)
    return users


@app.post(
    "/users", response_model=schemas.UserCreated, status_code=HTTP_201_CREATED, tags=["users"]
)
async def create_user(*, db: Session = Depends(get_db), user_in: schemas.UserCreating) -> Any:
    user_in_data = jsonable_encoder(user_in)
    user = await actions.user.get_by_email(db=db, email=user_in_data['email'])
    if user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User with same email already exist")
    db_user = User(**user_in_data)  # type: ignore
    db_user.set_password(user_in_data['password'])
    db_user.set_is_verified_false()
    db_user.set_is_superuser_false()
    db_user.set_created()
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
                      user_in: schemas.UserUpdate,
                      credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    current_user = await get_current_user(db=db, token=credentials.credentials)
    user = await actions.user.get_by_id(db=db, id=id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if (user.id == current_user.id or currenr_user.is_superuser):
        user = await actions.user.update(db=db, db_obj=user, obj_in=user_in)
        return user
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized for this resource.")


@app.get(
    "/users/{id}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
async def get_user(*, db: Session = Depends(get_db), id: UUID4,
                   credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    current_user = await get_current_user(db=db, token=credentials.credentials)
    user = await actions.user.get_by_id(db=db, id=id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if (user.id == current_user.id or currenr_user.is_superuser):
        return user
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized for this resource.")


@app.delete(
    "/users/{id}",
    response_model=schemas.HTTPNoContent,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
async def delete_user(*, db: Session = Depends(get_db), id: UUID4) -> Any:
    current_user = await get_current_user(db=db, token=credentials.credentials)
    user = await actions.user.get_by_id(db=db, id=id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if (user.id == current_user.id or currenr_user.is_superuser):
        user = await actions.user.remove(db=db, obj=user)
        return {'detail': 'No content'}
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized for this resource.")


@app.post(
    '/login',
    response_model=schemas.UserLogined,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["auth"],
)
async def login(*, db: Session = Depends(get_db), user_in: schemas.UserLogin):
    user_in_data = jsonable_encoder(user_in)
    user = await db.execute(select(User).filter(User.email==user_in_data['email']))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if (not user.verify_password(user_in_data['password'])):
        raise HTTPException(status_code=401, detail='Invalid password')
    access_token = await auth_handler.encode_token(user.email)
    refresh_token = await auth_handler.encode_refresh_token(user.email)
    user.set_last_login()
    await actions.user.update(db=db, db_obj=user, obj_in={'last_login': user.last_login})
    return {'access_token': access_token, 'refresh_token': refresh_token}


@app.get(
    '/refresh_token',
    response_model=schemas.AccessTokenRefreshed,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["auth"],
)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    print(refresh_token)
    new_token = await auth_handler.refresh_token(refresh_token)
    return {'new_access_token': new_token}


@app.post(
    '/secret',
    tags=["auth"],
)
def secret_data():
    return 'Secret data'


@app.get(
    '/notsecret',
    tags=["auth"],
)
def not_secret_data():
    return 'Not secret data'
