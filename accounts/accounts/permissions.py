from starlette.status import (HTTP_400_BAD_REQUEST,
                              HTTP_401_UNAUTHORIZED,)
from fastapi.security import HTTPBearer
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .auth import Auth
from . import actions


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
            status_code=HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


def is_superuser(func):
    print('###############')
    def wrapper(*args, **kwargs):
        db = kwargs.get['db']
        token = kwargs.get['token']
        print(db, token)
        func(*args, **kwargs)
    return wrapper
