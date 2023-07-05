import smtplib
from email.message import EmailMessage

from pydantic import EmailStr

from src import config


def send_mail(subject: str, body: str, email: EmailStr) -> None:
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = config.MAIL_FROM
    message['To'] = email
    message.set_content(body)

    with smtplib.SMTP_SSL(config.MAIL_SERVER, config.MAIL_PORT) as smtp:
        smtp.login(config.MAIL_FROM, config.MAIL_PASSWORD)
        smtp.send_message(message)
