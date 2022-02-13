from typing import Any, List

from fastapi import Depends, FastAPI#, HTTPException
# from pydantic import UUID4
# from sqlalchemy.orm import Session
# from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
# from fastapi.security import OAuth2PasswordBearer

# from .db import SessionLocal, engine

# Create all tables in the database.
# Comment this out if you using migrations.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session.
#def get_db():
#    try:
#        db = SessionLocal()
#        yield db
#    finally:
#        db.close()


@app.get("/")
def index():
    return {"message": "Hello world!"}
    