from typing import Optional, Union

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, \
    InvalidPasswordException, exceptions

from src.services import get_user_by_username
from src.database import get_user_db
from src.config import SECRET_KEY
from src.validators import validate_username, validate_email
from .models import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY
    reset_password_token_lifetime_seconds = 300
    verification_token_lifetime_seconds = 300

    async def validate_password(self, password: str, user: Union[schemas.UC, models.UP]) -> None:
        if len(password) < 6:
            raise InvalidPasswordException('Password should be at least 6 characters')
        return

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:

        await self.validate_password(user_create.password, user_create)

        await validate_username(user_create.username)

        existing_user = await self.user_db.get_by_email(user_create.email)
        await validate_email(user_create.email, existing_user)

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def authenticate(
        self,
        credentials: OAuth2PasswordRequestForm,
    ) -> Optional[models.UP]:
        try:
            user = await self.get_by_email(credentials.username)
        except exceptions.UserNotExists:
            user = await get_user_by_username(credentials.username)
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

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
