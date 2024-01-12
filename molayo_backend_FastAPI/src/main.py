from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes.users import users_router
from routes.posts import posts_router
from routes.deeplearning import deeplearning_router

""""
from connection import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

lifespan=lifespan,
"""

app = FastAPI(
        docs_url="/api/docs",
        redoc_url='/api/redoc',
        openapi_url='/api/openapi.json'
    )

origins = [
    "https://molayo.work"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/users")
app.include_router(posts_router, prefix="/api/posts")
app.include_router(deeplearning_router, prefix="/api")

