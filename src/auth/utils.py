from fastapi_users.jwt import generate_jwt
from pydantic import EmailStr
from starlette.requests import Request

from src.config import VERIFICATION_TOKEN_AUDIENCE
from src.config import VERIFICATION_TOKEN, VERIFICATION_TOKEN_LIFETIME
from src.tasks.tasks import register_email_verify


async def generate_token(username: str, email: EmailStr) -> str:
    token_data = {
        "sub": username,
        "email": email,
        "aud": VERIFICATION_TOKEN_AUDIENCE,
    }
    token = generate_jwt(
        token_data,
        VERIFICATION_TOKEN,
        VERIFICATION_TOKEN_LIFETIME,
    )
    return token

    # return await send_in_background([email], request, token)
