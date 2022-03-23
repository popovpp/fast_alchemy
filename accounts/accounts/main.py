import passlib

from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException, Security
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import (HTTP_201_CREATED, HTTP_404_NOT_FOUND,
                              HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                              HTTP_401_UNAUTHORIZED,)

from . import actions, models, schemas
from .db import SessionLocal, engine
from .models import User
from .auth import Auth
from . permissions import get_current_user, auth_required, get_current_user


app = FastAPI()


security = HTTPBearer()
auth_handler = Auth()


# Dependency to get DB session.
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        pass
#        db.close()


@app.get("/")
def index(request: Request):
    return {"message": "You are wellcome!"}


@app.get("/users", response_model=List[schemas.User], tags=["users"])
@auth_required('is_superuser')
async def list_users(*, db: Session = Depends(get_db), skip: int = 0, limit: int = 100,
                     credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    users = await actions.user.get_all(User, 'created',db=db, skip=skip, limit=limit)
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
@auth_required('is_superuser_or_is_owner')
async def update_user(*, db: Session = Depends(get_db), id: UUID4, 
                      user_in: schemas.UserUpdate,
                      credentials: HTTPAuthorizationCredentials = Security(security),
                      request: Request) -> Any:
    user = await actions.user.get_by_id(db=db, id=id)
    if not user:
        raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )
    user = await actions.user.update(db=db, db_obj=user, obj_in=user_in)
    return user


@app.get(
    "/users/{id}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=['users'],
)
@auth_required('is_superuser_or_is_owner')
async def get_user_by_id(*, db: Session = Depends(get_db), id: UUID4,
                   credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    user = await actions.user.get_by_attr(User, id, 'id', db=db,)
    if not user:
        raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )
    return user


@app.get(
    "/users/email/{email}",
    response_model=schemas.User,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
@auth_required('is_superuser_or_is_owner')
async def get_user_by_email(*, db: Session = Depends(get_db), email: str,
                   credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    user = await actions.user.get_by_attr(User, email, 'email', db=db)
    if not user:
        raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )
    return user


@app.delete(
    "/users/{id}",
    response_model=schemas.HTTPNoContent,
    responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
    tags=["users"],
)
@auth_required('is_superuser')
async def delete_user(*, db: Session = Depends(get_db), id: UUID4,
                      credentials: HTTPAuthorizationCredentials = Security(security)) -> Any:
    user = await actions.user.get_by_attr(User, id, 'id', db=db)
    if not user:
        raise HTTPException(
                        status_code=HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )
    user = await actions.user.remove(user, db=db)
    return {'detail': 'No content'}


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
async def refresh_token(*, db: Session = Depends(get_db),
                        credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = await auth_handler.refresh_token(refresh_token)
    await get_current_user(db=db, token=new_token)
    return {'new_access_token': new_token}


@app.post(
    "/superuser", response_model=schemas.UserCreated, status_code=HTTP_201_CREATED, tags=["users"]
)
async def create_superuser(*, db: Session = Depends(get_db), user_in: schemas.UserCreating) -> Any:
    
    superuser = await actions.user.get_by_attr(User, True, 'is_superuser', db=db)
    
    if not superuser:
        user_in_data = jsonable_encoder(user_in)
        user = await actions.user.get_by_email(db=db, email=user_in_data['email'])
        if user:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User with same email already exists")
        db_user = User(**user_in_data)  # type: ignore
        db_user.set_password(user_in_data['password'])
        db_user.set_is_verified_false()
        db_user.set_is_superuser_true()
        db_user.set_created()
        user = await actions.user.create(db=db, db_obj=db_user)
        return {'id': user.id, 'email': user.email}
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Superuser already exists")
