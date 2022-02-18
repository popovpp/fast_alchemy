from typing import Any, List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
# from fastapi.security import OAuth2PasswordBearer

from . import actions, models, schemas
from .db import SessionLocal, engine

# Create all tables in the database.
# Comment this out if you using migrations.
# models.Base.metadata.create_all(bind=engine)

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
async def list_posts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    users = await actions.user.get_all(db=db, skip=skip, limit=limit)
    return users


@app.post(
    "/users", response_model=schemas.UserCreated, status_code=HTTP_201_CREATED, tags=["users"]
)
async def create_user(*, db: Session = Depends(get_db), user_in: schemas.UserCreating) -> Any:
    user = await actions.user.create(db=db, obj_in=user_in)
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
