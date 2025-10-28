from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr

from app.models.user import User
from app.models.post import Post
from app.db.requests import PostRepository

router = APIRouter(prefix='/post')

