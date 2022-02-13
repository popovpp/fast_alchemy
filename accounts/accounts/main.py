from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from .user_manager import get_user_manager



fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello world!"}
