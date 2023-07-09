from os import environ

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = environ.get('SECRET_KEY')

# DataBase
DB_ENGINE = environ.get('DB_ENGINE')
DB_HOST = environ.get('DB_HOST')
DB_PORT = environ.get('DB_PORT')
DB_NAME = environ.get('DB_NAME')
DB_USER = environ.get('DB_USER')
DB_PASSWORD = environ.get('DB_PASSWORD')

# Auth
JWT_LIFETIME = 10 * 60
COOKIE_NAME = 'JWT'
TOKEN_AUDIENCE = environ.get('TOKEN_AUDIENCE')
VERIFICATION_TOKEN = environ.get('VERIFICATION_TOKEN')
VERIFICATION_TOKEN_LIFETIME = 5 * 60
VERIFICATION_TOKEN_AUDIENCE = environ.get('VERIFICATION_TOKEN_AUDIENCE')
RESET_PASSWORD_TOKEN = environ.get('RESET_PASSWORD_TOKEN')
RESET_PASSWORD_TOKEN_LIFETIME = 5 * 60
RESET_PASSWORD_TOKEN_AUDIENCE = environ.get('RESET_PASSWORD_TOKEN_AUDIENCE')

# SMTP
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
MAIL_FROM = environ.get('MAIL_FROM')
MAIL_PORT = environ.get('MAIL_PORT')
MAIL_SERVER = environ.get('MAIL_SERVER')

# CORS
CORS_ORIGIN = environ.get('CORS_ORIGIN').split(' ')
ALLOW_METHODS = ["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"]
ALLOW_HEADERS = ["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                 "Access-Control-Allow-Origin", "Authorization"]
