from pydantic import EmailStr
from starlette.requests import Request

from src.utils import send_mail


def register_email_verify(email: EmailStr, request: Request, token: str) -> None:
    subject = 'Verified email on FastAPI'
    body = f"""
    Verified email on FastAPI
    Confirmation link: {request.url}/{token}
    """
    send_mail(subject, body, email)


def reset_password_email(email: EmailStr, request: Request, token: str) -> None:
    subject = 'Reset password on FastAPI'
    body = f"""
    To reset your password, follow the link below
    {request.url}/{token}
    """
    send_mail(subject, body, email)
