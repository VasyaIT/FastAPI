from typing import Tuple

from fastapi import HTTPException
from fastapi_users.exceptions import InvalidVerifyToken
from fastapi_users.jwt import generate_jwt, decode_jwt
from jwt import PyJWTError
from pydantic import EmailStr
from starlette.status import HTTP_404_NOT_FOUND


def generate_token(
        sub: str, email: EmailStr, aud: str, secret: str, token_lifetime: int
) -> str:
    token_data = {
        "sub": sub,
        "email": email,
        "aud": aud,
    }
    token = generate_jwt(token_data, secret, token_lifetime, )
    return token


def decode_token(token: str, secret: str, aud: str) -> Tuple[str, EmailStr]:
    try:
        data = decode_jwt(token, secret, [aud])
    except PyJWTError:
        raise HTTPException(HTTP_404_NOT_FOUND)

    try:
        sub = data["sub"]
        email = data["email"]
    except KeyError:
        raise InvalidVerifyToken()

    return sub, email
