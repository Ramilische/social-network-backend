from sqlalchemy import select, update, delete, func
from pydantic import BaseModel, ConfigDict
from typing import List

from app.db.models import async_session, User, Post


class PostRepository:
    @staticmethod
    def serialize_post(post: Post):
        return {
            'post': {
                'author_id': post.author_id,
                'content': post.content,
                'photo_path': post.photo_path,
                #'create_time': post.create_time
                }
            }
    
    @classmethod
    async def add_post(cls, author_id: int, content: str = '', photo_path: str = ''):
        if content == '' and photo_path == '':
            return 400, {'message': 'Empty post'}
        
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.id == author_id))
            if not user:
                return 400, {'message': 'User with this ID does not exist'}
            
            new_post = Post(author_id=author_id, content=content, photo_path=photo_path)
            session.add(new_post)
            await session.commit()
            
            return 201, {'message': 'Post created'}
    
    @classmethod
    async def get_post(cls, post_id: int):
        async with async_session() as session:
            post = await session.scalar(select(Post).where(Post.id == post_id))
            if not post:
                return 400, {'message': 'Post with this ID does not exist'}
            
            return 200, PostRepository.serialize_post(post=post)
    
    @classmethod
    async def user_posts(cls, user_id: int, start: int = 1, end: int = 100):
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.id == user_id))
            if not user:
                return 400, {'message': 'User with this ID does not exist'}

            posts = await session.scalars(select(Post).where(Post.author_id == user_id).limit(end))
            
            return 200, list([PostRepository.serialize_post(post) for post in posts])[start - 1:]
            
