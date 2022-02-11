from typing import Optional

from pydantic import BaseModel, UUID4


# Shared properties
class PostBase(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None


# Properties to receive via API on creation
class PostCreate(PostBase):
    title: str
    body: str


# Properties to receive via API on update
class PostUpdate(PostBase):
    pass


class PostInDBBase(PostBase):
    id: Optional[UUID4] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Post(PostInDBBase):
    pass


# Additional properties stored in DB
class PostInDB(PostInDBBase):
    pass


class HTTPErrorBase(BaseModel):
    detail: Optional[str] = None


class HTTPError(HTTPErrorBase):
    pass


class HTTPNoContentBase(BaseModel):
    detail: Optional[str] = None


class HTTPNoContent(HTTPNoContentBase):
    pass
    