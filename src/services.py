from typing import Callable

from sqlalchemy import select, Select, update, Update

from .database import async_session_maker
from src.auth.models import User
from .base_models import Base


async def get_objects(obj: Base) -> Callable[[Select, bool], Base | None]:
    return await get_model_or_none(select(obj), False)


async def get_object_by_id(obj: Base, obj_id: int) -> Callable[[Select, bool], Base | None]:
    query = select(obj).where(obj.id == int(obj_id))
    return await get_model_or_none(query, True)


async def get_user_by_username(username: str) -> Callable[[Select, bool], Base | None]:
    query = select(User).where(User.username == username)
    return await get_model_or_none(query, True)


async def update_user_username(
        old_username: str, new_username: str
) -> Callable[[Update, bool], Base | None]:
    stmt = (update(User).values(username=new_username)
            .where(User.username == old_username).returning(User.username))
    return await update_insert_delete_model_or_none(stmt, True)


async def get_model_or_none(query: Select, one: bool) -> Base | None:
    async with async_session_maker() as session:
        result = await session.execute(query)

    try:
        if one:
            [model] = result.scalars().all()
        else:
            model = result.scalars().all()
    except ValueError:
        return
    return model


async def update_insert_delete_model_or_none(statement: Update, one: bool) -> Base | None:
    async with async_session_maker() as session:
        result = await session.execute(statement)
        await session.commit()

    try:
        if one:
            [model] = result.scalars().all()
        else:
            model = result.scalars().all()
    except ValueError:
        return
    return model
