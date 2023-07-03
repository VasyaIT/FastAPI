from typing import Callable

from sqlalchemy import select, Select

from .database import async_session_maker
from src.auth.models import User
from .base_models import Base


async def get_object_by_id(obj: Base, obj_id: int) -> Callable[[Select], Base | None]:
    query = select(obj).where(obj.id == int(obj_id))
    return await get_model_or_none(query)


async def get_user_by_username(username: str) -> Callable[[Select], Base | None]:
    query = select(User).where(User.username == username)
    return await get_model_or_none(query)


async def get_model_or_none(query: Select) -> Base | None:
    async with async_session_maker() as session:
        result = await session.execute(query)
    try:
        [model] = result.scalars().all()
    except ValueError:
        return None
    return model
