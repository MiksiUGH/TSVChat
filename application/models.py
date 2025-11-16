from sqlalchemy import create_engine, ForeignKey, Engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship, DeclarativeBase
from typing import List, Optional


ENGINE: Engine = create_engine('sqlite:///tsv_user.db')
"""Движок базы данных SQLite."""

MAIN_SESSION = sessionmaker(bind=ENGINE)
"""Фабрика сессий для работы с базой данных."""


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


class User(Base):
    """
    Модель пользователя системы.

    Attributes:
        id (Mapped[int]): Уникальный идентификатор пользователя
        username (Mapped[str]): Имя пользователя
        user_profile (Mapped[UserProfile]): Профиль пользователя (один-к-одному)
        messages (Mapped[List[UserMessage]]): Сообщения пользователя (один-ко-многим)
    """
    __tablename__: str = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()

    user_profile: Mapped[Optional['UserProfile']] = relationship(
        back_populates='user',
        uselist=False,
        cascade="all, delete-orphan"
    )
    messages: Mapped[List['UserMessage']] = relationship(
        back_populates='user',
        cascade="all, delete-orphan"
    )


class UserProfile(Base):
    """
    Профиль пользователя с дополнительной информацией.

    Attributes:
        id (Mapped[int]): Уникальный идентификатор профиля
        user_info (Mapped[str]): Дополнительная информация о пользователе
        user_password (Mapped[str]): Пароль пользователя
        user_id (Mapped[int]): Внешний ключ к пользователю
        user_state (Mapped[bool]): Состояние пользователя (активен/неактивен)
        user (Mapped[User]): Связанный пользователь
    """
    __tablename__: str = 'user_profiles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_info: Mapped[str] = mapped_column()
    user_password: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    user_state: Mapped[bool] = mapped_column(default=True)

    user: Mapped['User'] = relationship(back_populates='user_profile')


class UserMessage(Base):
    """
    Сообщения пользователей.

    Attributes:
        id (Mapped[int]): Уникальный идентификатор сообщения
        date (Mapped[str]): Дата и время отправки сообщения
        message (Mapped[str]): Текст сообщения
        user_name (Mapped[str]): Имя пользователя-отправителя (внешний ключ)
        user (Mapped[User]): Связанный пользователь-отправитель
    """
    __tablename__: str = 'user_messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column()
    message: Mapped[str] = mapped_column()
    user_name: Mapped[str] = mapped_column(ForeignKey('users.username'))

    user: Mapped['User'] = relationship(back_populates='messages')
