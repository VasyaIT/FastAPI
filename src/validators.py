from typing import Callable, Any

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.auth.models import User
from .services import get_user_by_username


def auth_form_exception(field: str, message: str) -> HTTPException:
    raise HTTPException(
        HTTP_400_BAD_REQUEST,
        {
            "detail": [
                {
                    "loc": [
                        "body",
                        f"{field}"
                    ],
                    "msg": f"{message}",
                    "type": f"value_error.{field}"
                }
            ]
        }
    )


async def validate_username(username: str) -> None:
    if '@' in username:
        auth_form_exception('username', 'username must not contain @')

    if await get_user_by_username(username):
        auth_form_exception('username', 'user with this username already exists')


async def validate_email(existing_user: User) -> None:
    if existing_user:
        auth_form_exception('email', 'user with this email already exists')


async def check_passwords(
        is_math_old_password: bool, new_password: str, new_password_confirm: str
) -> None:
    if not is_math_old_password:
        auth_form_exception('old_password', 'old password does not match the current')
    if new_password != new_password_confirm:
        auth_form_exception('new_password', 'passwords do not match')
