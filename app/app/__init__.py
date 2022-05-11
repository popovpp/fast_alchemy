"""
NAME
====
app — Приложение, содержащее общий для всех компонентов конфигурационный файл `config.py`,
      а также модуль `actions.py` содержащий класс `BaseActions`, в котором представлены 
      базовые CRUD операции с объектами БД

VERSION
=======
0.1.0

SYNOPSIS
========

```
from app.app.config import settings


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI,
                             pool_pre_ping=True, echo=True)
```

```
from app.app import actions


ModelType = TypeVar("ModelType", bound=schemas.User)
CreateSchemaType = TypeVar("CreateSchemaType", bound=schemas.UserCreating)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class UserActions(actions.BaseActions[schemas.User, schemas.UserCreated, schemas.UserUpdate]):
    pass


user_actions = UserActions()
```

DESCRIPTION
===========
Дли использования CRUD операций необходимо создать класс - наследник от `BaseActions`, 
определив при необходимости три основные схемы: `ModelType`, `CreateSchemaType` и 
`UpdateSchemaType`. Затем необходимо создать экземпляр вновь созданного класа.

CLASS
=====
"""

__version__ = '0.1.0'
