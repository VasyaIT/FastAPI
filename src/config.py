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

# JWT
JWT_LIFETIME = 600
