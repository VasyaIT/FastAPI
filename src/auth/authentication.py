from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend

from src.config import SECRET_KEY, JWT_LIFETIME, COOKIE_NAME, TOKEN_AUDIENCE

cookie_transport = CookieTransport(cookie_name=COOKIE_NAME, cookie_max_age=JWT_LIFETIME)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET_KEY, lifetime_seconds=JWT_LIFETIME, token_audience=[TOKEN_AUDIENCE]
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
