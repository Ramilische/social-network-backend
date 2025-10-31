from os import getenv
import pathlib
from datetime import datetime

import dotenv
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import ForeignKey, String, Integer, ARRAY, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

BASE_URL = pathlib.Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(env_file=BASE_URL.joinpath('.env/db.env'))

    def get_db_url_pg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings() # type: ignore
print(settings.get_db_url_pg())
engine = create_async_engine(url=settings.get_db_url_pg(), echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile: Mapped['Profile'] = relationship(back_populates='user')


class Profile(Base):
    __tablename__ = 'profiles'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    user: Mapped['User'] = relationship(back_populates='profile')

    name: Mapped[str]
    surname: Mapped[str] = mapped_column(String, nullable=True)
    photo_path: Mapped[str] = mapped_column(String, nullable=True)

    city_id: Mapped[int] = mapped_column(ForeignKey('cities.id'), default=1)
    city: Mapped['City'] = relationship(back_populates='people')

    status: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    posts: Mapped[List['Post'] | None] = relationship(back_populates='author')

    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), onupdate=True)


class City(Base):
    __tablename__ = 'cities'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    population: Mapped[int] = mapped_column(Integer)
    country_id: Mapped[int] = mapped_column(ForeignKey('countries.id'))
    country: Mapped['Country'] = relationship(back_populates='cities')
    people: Mapped[List['Profile']] = relationship(back_populates='city')


class Country(Base):
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    cities: Mapped[List['City']] = relationship(back_populates='country')


class Salt(Base):
    __tablename__ = 'spices'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    salt: Mapped[str] = mapped_column(String)


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('profiles.user_id'))
    author: Mapped['Profile'] = relationship(back_populates='posts')
    content: Mapped[str] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str] = mapped_column(String, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)