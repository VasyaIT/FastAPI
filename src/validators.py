from fastapi_users.exceptions import UserAlreadyExists

from src.auth.models import User
from .services import get_user_by_username


async def validate_username(username: str) -> None:
    if '@' in username:
        raise UserAlreadyExists('weg')
    if await get_user_by_username(username):
        raise UserAlreadyExists('ergerg')


async def validate_email(username: str, user: User) -> None:
    if '@' not in username:
        raise UserAlreadyExists('weg')
    if user is not None:
        raise UserAlreadyExists('weg')
