from typing import List, Dict, Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.exceptions import UserAlreadyExists, InvalidVerifyToken
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette import status
from starlette.responses import RedirectResponse

from src.services import update_user, get_objects, get_object_by_username
from src.validators import auth_form_exception
from .authentication import auth_backend
from .manager import get_user_manager
from .models import User
from .schemas import UserCreate, UserReadUpdate, UserPasswordChange

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

get_user_or_401 = fastapi_users.current_user()
get_user_or_none = fastapi_users.current_user(optional=True)
is_superuser_or_403 = fastapi_users.current_user(superuser=True)

auth_router = APIRouter(prefix='/auth', tags=['auth'])
user_router = APIRouter(prefix='/account', tags=['users'])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, name="register:register")
async def register(
        request: Request,
        user_create: UserCreate,
        background_tasks: BackgroundTasks,
        user_manager=Depends(get_user_manager),
        user: User = Depends(get_user_or_none)
):
    if user:
        return RedirectResponse('/', 303)
    try:
        return await user_manager.create(
            user_create, request=request, background_tasks=background_tasks
        )
    except UserAlreadyExists:
        raise auth_form_exception('username', 'user with this username already exists')


@auth_router.get(
    '/register/{token}',
    status_code=status.HTTP_202_ACCEPTED,
    name='register:verify',
)
async def verified(
        token: str,
        request: Request,
        user_manager=Depends(get_user_manager)
):
    try:
        return await user_manager.email_verified(token, request)
    except InvalidVerifyToken:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'token is invalid')


@auth_router.post('/change_password')
async def password_change(
        data: UserPasswordChange,
        user: User = Depends(get_user_or_401),
        user_manager=Depends(get_user_manager)
):
    return await user_manager.check_password(data, user)


@user_router.get('/me', name='user:me', response_model=UserReadUpdate)
async def user_me(user: User = Depends(get_user_or_401)):
    return user


@user_router.patch('/me/update', name='user:update')
async def user_me_update(data: UserReadUpdate, user: User = Depends(get_user_or_401)):
    await update_user(user.id, data.dict())
    return {'success': 'account updated successfully'}


@user_router.get(
    '/users', name='user:users',
    dependencies=[Depends(is_superuser_or_403)],
    response_model=List[UserReadUpdate]
)
async def user_list():
    return await get_objects(User)


@user_router.get('/user/{username}', name='user:user', response_model=UserReadUpdate)
async def user_account(username: str):
    user = await get_object_by_username(User, username)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return user
