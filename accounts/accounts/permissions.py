from starlette.status import (HTTP_400_BAD_REQUEST,
                              HTTP_401_UNAUTHORIZED,)
from fastapi.security import HTTPBearer
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from functools import wraps

from .auth import Auth
from . import actions
from .models import User


security = HTTPBearer()
auth_handler = Auth()


permissions = {
    'is_superuser': 'is_superuser',
    'is_authenticated': 'is_authenticated',
    'is_owner': 'is_owner',
    'is_superuser_or_is_owner': 'is_superuser_or_is_owner',
}


async def get_current_user(db: Session, token: str = Depends(security)):
    email = await auth_handler.decode_token(token)
    user = await actions.user.get_by_attr(User, email, 'email', db=db)
    await db.close()
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


def auth_required(permissions_item):
    def auth_required_wrapper(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = await get_current_user(db=kwargs.get('db'),
                                                  token=kwargs.get('credentials').credentials)
            if permissions_item == 'is_superuser':
                if not current_user.is_superuser:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                    )
            elif permissions_item == 'is_owner':
                if not (kwargs.get('email')==current_user.email or kwargs.get('id')==current_user.id):
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                    )
            elif permissions_item == 'is_superuser_or_is_owner':
                if not (current_user.is_superuser or
                       (kwargs.get('email')==current_user.email or kwargs.get('id')==current_user.id)):
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                    )
            return await func(*args, **kwargs)    
        return wrapper
    return auth_required_wrapper
