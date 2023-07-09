from typing import Callable, Dict, Any, Union, List

from fastapi import HTTPException
from sqlalchemy import select, Select, update, Update, insert, Insert
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_400_BAD_REQUEST

from src.bots.models import Bot
from .database import async_session_maker
from src.auth.models import User
from .base_models import Base


async def get_objects(obj: Base) -> Callable[[Select, bool], Base | None]:
    return await get_model_or_none(select(obj), False)


async def get_object_by_id(obj: Base, obj_id: int) -> Callable[[Select, bool], Base | None]:
    query = select(obj).where(obj.id == int(obj_id))
    return await get_model_or_none(query, True)


async def get_object_by_username(obj: Base, username: str) -> Callable[[Select, bool], Base | None]:
    query = select(obj).where(obj.username == username)
    return await get_model_or_none(query, True)


async def update_user(user_id: int, data: Dict[str, Any]) -> Callable[[Update | Insert], None]:
    stmt = (update(User).values(data).where(User.id == user_id))
    return await update_insert_delete_model_or_none(stmt)


async def get_bot_by_username(username: str, user_id: int) -> Callable[[Select, bool], Base | None]:
    query = select(Bot).where(Bot.username == username, Bot.user_id == user_id)
    print(query)
    return await get_model_or_none(query, True)


async def insert_bot(data: Dict[str, Any]) -> Callable[[Update | Insert], None]:
    stmt = insert(Bot).values(data)
    return await update_insert_delete_model_or_none(stmt)


async def get_model_or_none(query: Select, one: bool) -> Union[Base, List[Base], None, Any]:
    async with async_session_maker() as session:
        result = await session.execute(query)

    try:
        if one:
            model = result.scalar()
        else:
            model = result.scalars().all()
    except ValueError:
        return
    return model


async def update_insert_delete_model_or_none(statement: Update | Insert) -> None:
    async with async_session_maker() as session:
        try:
            await session.execute(statement)
        except IntegrityError:
            raise HTTPException(HTTP_400_BAD_REQUEST, 'This bot has already been added')
        await session.commit()
