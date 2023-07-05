from fastapi import FastAPI, Depends, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .services import get_object_by_id
from src.auth.routers import get_user_or_401
from .config import SECRET_KEY, CORS_ORIGIN
from src.auth.models import User
from .database import async_session_maker
from src.auth.schemas import UserCreate, UserReadUpdate
from src.auth.routers import fastapi_users
from src.auth.authentication import auth_backend
from src.auth.routers import auth_router, user_router


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=5 * 60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])


@app.get('/')
async def foo():
    pass


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        async with async_session_maker() as session:
            request.state.db = session
        response = await call_next(request)
    # except Exception as e:
    #     print(repr(e))
    #     response = Response("Internal server error", status_code=500)
    finally:
        await request.state.db.close()
    return response
