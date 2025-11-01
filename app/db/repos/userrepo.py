from sqlalchemy import select, update, delete, func
from pydantic import BaseModel, ConfigDict
from typing import List

from app.db.models import async_session, User, Profile, City, Salt
from app.utils.password import hash_password, make_salt


class UserRepository:
    @staticmethod
    def serialize_user(user: User | None, profile: Profile | None, city: City | None):
        return {
            'id': user.id if user else None,
            'username': user.username if user else None,
            'name': profile.name if profile else None,
            'surname': profile.surname if profile else None,
            'photo_path': profile.photo_path if profile else None,
            'city': city.name if city else None,
            'status': profile.status if profile else None,
            'description': profile.description if profile else None
            }
    
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
                result = UserRepository.serialize_user(user=user, profile=profile, city=city)
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
                result.append(UserRepository.serialize_user(user=user, profile=profile, city=city))
                
            return 200, result