from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr

from app.models.user import User
from app.models.post import Post
from app.db.requests import PostRepository

router = APIRouter(prefix='/post')


class CreatePostSchema(BaseModel):
    author_id: int = Field(default=0, description='ID автора поста')
    content: str = Field(default='', description='Текст поста')
    photo_path: str = Field(default='Путь до фото (временно)')


class ShowPostSchema(BaseModel):
    author_id: int = Field(default=0, description='ID автора поста')
    content: str = Field(default='', description='Текст поста')
    photo_path: str = Field(default='Путь до фото (временно)')
    create_time: datetime = Field(description='Время создания поста')


@router.post('/create')
async def create_post(post: CreatePostSchema):
    code, message = await PostRepository.add_post(author_id=post.author_id, content=post.content, photo_path=post.photo_path)
    return JSONResponse(status_code=code, content=message)


@router.get('/show/{post_id}')
async def show_post(post_id: int):
    code, post = await PostRepository.get_post(post_id=post_id)
    return JSONResponse(status_code=code, content=post)


@router.get('/allposts')
async def show_all_posts(user_id: int, start: int = 1, end: int = 100):
    code, posts = await PostRepository.user_posts(user_id=user_id, start=start, end=end)
    return JSONResponse(status_code=code, content=posts)
    