from pydantic import BaseModel, Field


class Post(BaseModel):
    id: int
    title: str = Field(description='Заголовок поста')
    text: str = Field(description='Текст поста')
    photo_path: str = Field(description='Название фото поста(если есть)')
    is_published: bool = Field(default=True, description='Опубликован ли пост')
    rating: int = Field(default=0, description='Рейтинг поста (кол-во пальцев вверх)')