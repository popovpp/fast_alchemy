import datetime

from fastapi_users import models


class User(models.BaseUser):
    first_name: Optional[str]
    last_name: Optionnal[str]
    birthdate: Optional[datetime.date]


class UserCreate(models.BaseUserCreate):
    first_name: Optional[str]
    last_name: Optionnal[str]
    birthdate: Optional[datetime.date]


class UserUpdate(models.BaseUserUpdate):
    first_name: Optional[str]
    last_name: Optionnal[str]
    birthdate: Optional[datetime.date]


class UserDB(User, models.BaseUserDB):
    first_name: Optional[str]
    last_name: Optionnal[str]
    birthdate: Optional[datetime.date]
