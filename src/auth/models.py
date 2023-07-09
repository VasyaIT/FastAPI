from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base_models import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, index=True, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(length=15), unique=True, index=True, nullable=False
    )
    bots = relationship('Bot', backref='user', lazy='selectin')

    # lazy = selectin is overridden so that lazy database requests are not loaded
    # Because here the database works completely asynchronously
