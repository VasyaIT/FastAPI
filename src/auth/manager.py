from typing import Optional, Union, Dict

from dns.message import make_response
from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, \
    InvalidPasswordException, exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.jwt import decode_jwt
from jwt import PyJWTError
from sqlalchemy.exc import IntegrityError
from starlette.background import BackgroundTasks
from starlette.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.services import get_object_by_username
from src.database import get_user_db
from src import config, validators
from src.tasks.tasks import register_email_verify
from .models import User
from .schemas import UserPasswordChange
from .utils import generate_token, decode_token


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = config.RESET_PASSWORD_TOKEN
    verification_token_secret = config.VERIFICATION_TOKEN
    verification_token_lifetime_seconds = config.VERIFICATION_TOKEN_LIFETIME
    verification_token_audience = config.VERIFICATION_TOKEN_AUDIENCE
    reset_password_token_lifetime_seconds = config.RESET_PASSWORD_TOKEN_LIFETIME
    reset_password_token_audience = config.RESET_PASSWORD_TOKEN_AUDIENCE

    async def validate_password(self, password: str, user: Union[schemas.UC, models.UP]) -> None:
        if len(password) < 6:
            raise validators.auth_form_exception(
                'password', 'password should be at least 6 characters'
            )
        return

    async def create(
        self,
        user_create: schemas.UC,
        background_tasks: BackgroundTasks,
        request: Optional[Request] = None,
    ) -> Dict[str, str]:

        await self.validate_password(user_create.password, user_create)

        await validators.validate_username(user_create.username)

        existing_user = await self.user_db.get_by_email(user_create.email)
        await validators.validate_email(existing_user)

        request.session["hashed_password"] = self.password_helper.hash(user_create.password)

        token = generate_token(
            user_create.username,
            user_create.email,
            config.VERIFICATION_TOKEN_AUDIENCE,
            config.VERIFICATION_TOKEN,
            config.VERIFICATION_TOKEN_LIFETIME
        )

        background_tasks.add_task(register_email_verify, user_create.email, request, token)

        return {'success': 'verify email sent'}

    async def authenticate(
        self,
        credentials: OAuth2PasswordRequestForm,
    ) -> Optional[models.UP]:
        try:
            user = await self.get_by_email(credentials.username)
        except exceptions.UserNotExists:
            user = await get_object_by_username(User, credentials.username)
            if user is None:
                self.password_helper.hash(credentials.password)
                return
        if user:
            verified, updated_password_hash = self.password_helper.verify_and_update(
                credentials.password, user.hashed_password
            )
            if not verified:
                return
            if updated_password_hash is not None:
                await self.user_db.update(user, {"hashed_password": updated_password_hash})

            return user

    async def email_verified(
            self, token: str, request: Optional[Request] = None
    ) -> RedirectResponse:
        username, email = decode_token(
            token,
            config.VERIFICATION_TOKEN,
            config.VERIFICATION_TOKEN_AUDIENCE,
        )

        user_dict = dict()
        user_dict['username'] = username
        user_dict['email'] = email

        session_password = request.session['hashed_password']
        if not session_password:
            raise exceptions.InvalidVerifyToken()

        user_dict['hashed_password'] = session_password
        del request.session['hashed_password']

        try:
            created_user = await self.user_db.create(user_dict)
        except IntegrityError:
            validators.auth_form_exception('username', 'user with this username already exists')

        token = generate_token(
            created_user.id,
            created_user.email,
            config.TOKEN_AUDIENCE,
            config.SECRET_KEY,
            config.JWT_LIFETIME
        )

        response = RedirectResponse('/')
        response.set_cookie('JWT', token, config.JWT_LIFETIME)
        return response

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        register_email_verify(user.email, request, token)
        return {'success': 'reset password email sent'}

    async def check_password(self, data: UserPasswordChange, user: User) -> Dict[str, str]:
        is_math_old_password, _ = self.password_helper.verify_and_update(
            data.old_password, user.hashed_password
        )
        await validators.check_passwords(
            is_math_old_password, data.new_password, data.new_password_confirm
        )
        await self.validate_password(data.new_password, user)

        new_hashed_password = self.password_helper.hash(data.new_password)
        await self.user_db.update(user, {'hashed_password': new_hashed_password})

        return {'success': 'password changed'}


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
