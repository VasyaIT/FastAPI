from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
# from debug_toolbar.middleware import DebugToolbarMiddleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from src.bots.routers import bot_router
from src.bots.models import Bot
from src.bots.schema import BotRead
from .services import get_object_by_id
from .config import SECRET_KEY, CORS_ORIGIN, ALLOW_METHODS, ALLOW_HEADERS
from src.auth.models import User
from .database import async_session_maker
from src.auth.schemas import UserCreate, UserReadUpdate
from src.auth.routers import fastapi_users, auth_router, user_router, get_user_or_401
from src.auth.authentication import auth_backend


app = FastAPI()  # debug=True

# app.add_middleware(
#     DebugToolbarMiddleware,
#     panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
# )

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=5 * 10)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=ALLOW_METHODS,
    allow_headers=ALLOW_HEADERS,
)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(bot_router)


@app.get('/')
async def main():
    pass
