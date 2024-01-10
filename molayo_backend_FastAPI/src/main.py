from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.users import users_router
from routes.posts import posts_router
from routes.deeplearning import deeplearning_router
from connection import conn
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "https://api.molayo.work",
    "https://molayo.work"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/users")
app.include_router(posts_router, prefix="/posts")
app.include_router(deeplearning_router)



