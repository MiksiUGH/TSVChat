from sqlalchemy import create_engine, ForeignKey, select, func, Select, Engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship, DeclarativeBase
import datetime
from typing import List


ENGINE: Engine = create_engine('sqlite:///tsv_user.db')
MAIN_SESSION = sessionmaker(bind=ENGINE)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


class User(Base):
    """Модель пользователя системы."""
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()

    user_profile: Mapped['UserProfile'] = relationship(back_populates='user', uselist=False)
    messages: Mapped[List['UserMessage']] = relationship(back_populates='user')


class UserProfile(Base):
    """Профиль пользователя с дополнительной информацией."""
    __tablename__ = 'user_profiles'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_info: Mapped[str] = mapped_column()
    user_password: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)

    user: Mapped['User'] = relationship(back_populates='user_profile')


class UserMessage(Base):
    """Сообщения пользователей."""
    __tablename__ = 'user_messages'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column()
    message: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['User'] = relationship(back_populates='messages')
