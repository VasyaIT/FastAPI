import jwt
from fastapi_users.jwt import decode_jwt
from starlette.requests import Request

from .services import get_object_by_id
from src.auth.models import User
from .config import SECRET_KEY, COOKIE_NAME


async def is_authenticate(request: Request) -> User | bool:
    """
    Checks the user by the JWT token and returns the user object if the token is valid
    Otherwise returns False
    """
    token = request.cookies.get(COOKIE_NAME)

    if token:
        try:
            data = decode_jwt(token, SECRET_KEY, ['jwt'])
        except jwt.PyJWTError:
            return False

        try:
            user_id = data["sub"]
        except KeyError:
            raise False

        user = await get_object_by_id(User, user_id)

        return user if user else False
    return False
