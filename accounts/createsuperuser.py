import asyncio
from typing import Any
import getpass

from fastapi import Depends
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from typing import TypeVar
from sqlalchemy.orm import Session

from accounts import models, schemas
from accounts.db import SessionLocal
from accounts.models import User

from accounts.main import user_actions


async def create_superuser(*, db=SessionLocal()) -> Any:
    
    superuser = await user_actions.get_by_attr_first(User, True, 'is_superuser', db=db)
    
    if not superuser:
        user_in = {}
        user_in['email'] = input('Введите email:')
        user_in['password'] = getpass.getpass('Введите пароль:')

        user_in_data = jsonable_encoder(user_in)
        user = await user_actions.get_by_attr_first(User, user_in_data['email'], 'email', db=db)
        
        if user:
            print("User with same email already exists")
        else:
            db_user = User(**user_in_data)
            db_user.set_password(user_in_data['password'])
            db_user.set_is_verified_false()
            db_user.set_is_superuser_true()
            db_user.set_created()
            user = await user_actions.create(db=db, db_obj=db_user)
            print('Superuser was creaed.')
            print({'id': user.id, 'email': user.email})
    else:
        print("Superuser already exists")


def main():
    asyncio.run(create_superuser())


if __name__=="__main__":
    main()
