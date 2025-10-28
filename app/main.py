from contextlib import asynccontextmanager
import pathlib
from fastapi import FastAPI, status, Response
from app.routers import posts_router, users_router
from app.db.models import init_db


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('App is ready')
    yield


app = FastAPI(title='Соцсеть', lifespan=lifespan)

app.include_router(users_router.router)
app.include_router(posts_router.router)