from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr

from app.models.user import User
from app.db.requests import UserRepository

router = APIRouter(prefix='/user')


class RegisterSchema(BaseModel):
    username: str = Field(default='example', min_length=3, description='Имя пользователя')
    email: EmailStr = Field(default='example@gmail.com', description='Адрес электронной почты')
    password: str = Field(default='password', max_length=64, repr=False, description='Пароль')
    name: str = Field(default='Иван', min_length=2, description='Имя')


class LoginSchema(BaseModel):
    username: str = Field(default='example', min_length=3, description='Имя пользователя')
    password: str = Field(default='password', max_length=64, repr=False, description='Пароль')


@router.post('/register', status_code=status.HTTP_201_CREATED, summary='Создать нового пользователя')
async def create_user(user: RegisterSchema):
    code, message = await UserRepository.add_user(user.username, user.email, user.password, user.name)
    return JSONResponse(status_code=code, content=message)


@router.post('/authorize', status_code=status.HTTP_200_OK, summary='Логин')
async def login(user: LoginSchema):
    code, message = await UserRepository.check_user(user.username, user.password)
    return JSONResponse(status_code=code, content=message)


@router.get('/profile/{username}')
async def profile(username: str):
    profile_info = await UserRepository.get_profile(username)
    headers = {'Access-Control-Allow-Origin': 'http://localhost:3000'}
    return JSONResponse(content=profile_info, headers=headers)