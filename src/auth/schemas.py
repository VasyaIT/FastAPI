from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr, BaseModel


class BaseUser(CreateUpdateDictModel):
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserRead(CreateUpdateDictModel):
    username: str

    class Config:
        orm_mode = True


class UserCreate(BaseUser):
    password: str


class UserUpdate(CreateUpdateDictModel):
    password: str

    class Config:
        orm_mode = True
