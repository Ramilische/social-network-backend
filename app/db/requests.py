from sqlalchemy import select, update, delete, func
from pydantic import BaseModel, ConfigDict
from typing import List

from app.db.models import async_session, User, Profile, Post, City, Country, Salt
from app.utils.password import hash_password, make_salt


class UserRepository:
    @classmethod
    async def add_user(cls, username: str, email: str, password: str, name: str):
        """
        Проверяет, существует ли пользователь. Если нет - создает запись в БД.
        Функция используется при регистрации
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.username == username))
            if user:
                return 200, {'message': 'User already exists'}

            salt = await make_salt()
            hashed_password = await hash_password(password, salt)

            new_user = User(username=username, email=email, password=hashed_password, is_active=True)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            new_profile = Profile(name=name, user=new_user)

            new_salt = Salt(user_id=new_user.id, salt=salt)
            session.add(new_salt)
            session.add(new_profile)
            await session.commit()

            return 201, {'message': 'User created'}

    @classmethod
    async def check_user(cls, username: str, password: str):
        """
        Проверяет соответствие введенных юзернейма и пароля с теми, что в БД.
        Функция используется при авторизации и смене пароля
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.username == username))
            if not user:
                return 400, {'message': 'Wrong username or password'}

            salt_obj = await session.scalar(select(Salt).where(Salt.user_id == user.id))
            if not salt_obj:
                return 502, {'message': 'Server error'}

            hashed_password = await hash_password(password=password, salt=salt_obj.salt)
            if hashed_password == user.password:
                return 200, {'message': 'Successful authorization'}
            return 400, {'message': 'Wrong username or password'}

    @classmethod
    async def get_profile(cls, username: str):
        async with async_session() as session:
            profile = await session.scalar(select(Profile).join(User, Profile.user_id == User.id).where(User.username == username))
            user = await session.scalar(select(User).where(User.username == username))
            city = await session.scalar(select(City).where(City.id == profile.city_id)) if profile else None
            result = dict()
            if profile:
                result = {
                    'username': user.username if user else None,
                    'name': profile.name,
                    'surname': profile.surname,
                    'photo_path': profile.photo_path,
                    'city': city.name if city else None,
                    'status': profile.status,
                    'description': profile.description
                    }
            return result
    
    @classmethod
    async def get_all_profiles(cls):
        async with async_session() as session:
            users = await session.scalars(select(User))
            profiles = await session.scalars(select(Profile).join(User, Profile.user_id == User.id))
            result = list()
            for item in tuple(zip(users, profiles)):
                user: User = item[0]
                profile: Profile = item[1]
                city = await session.scalar(select(City).where(City.id == profile.city_id))
                result.append({
                    'username': user.username if user else None,
                    'name': profile.name,
                    'surname': profile.surname,
                    'photo_path': profile.photo_path,
                    'city': city.name if city else None,
                    'status': profile.status,
                    'description': profile.description
                    })
                
            return 200, result


class PostRepository:
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
            
            return 200, {'post', post}
    
    @classmethod
    async def user_posts(cls, user_id: int, start: int = 1, end: int = 100):
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.id == user_id))
            if not user:
                return 400, {'message': 'User with this ID does not exist'}

            posts = await session.scalars(select(Post).where(Post.author_id == user_id).limit(end))
            
            return list(posts)[start - 1:]
            
