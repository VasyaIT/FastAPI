from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import SECRET_KEY
from .utils import is_authenticate
from src.auth.models import User
from .database import async_session_maker
from src.auth.schemas import UserCreate, UserRead, UserUpdate
from src.auth.routers import fastapi_users
from src.auth.authentication import auth_backend


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )


@app.get('/')
async def foo(request: Request):
    user = await is_authenticate(request)
    if user:
        return user.username
    return {'': ''}


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        async with async_session_maker() as session:
            request.state.db = session
        response = await call_next(request)
    finally:
        await request.state.db.close()
    return response
