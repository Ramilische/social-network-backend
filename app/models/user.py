from pydantic import BaseModel, Field, EmailStr
from uuid import UUID


class User(BaseModel):
    id: int
    username: str = Field(default='example', min_length=3, description='Имя пользователя')
    email: EmailStr = Field(default='example@gmail.com', description='Адрес электронной почты')
    password: str = Field(default='password', max_length=64, repr=False, description='Пароль')
    is_active: bool = Field(default=True, description='Активен пользователь или просто занимает место в БД')
    points: int