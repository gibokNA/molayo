from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship, Column, VARCHAR

if TYPE_CHECKING:
    from .posts import Post, Comment

class Token(BaseModel):
    access_token: str
    token_type: str


class User_Base(SQLModel):
    id: int
    username: str = Field(sa_column=Column("username", VARCHAR, unique=True, index=True))
    nickname: str = Field()

    post_count: int = 0 # 정식 경로로 삭제된게 아닌 cascade로 삭제되면 데이터 무결성이 깨짐. 계속 추적하면 무결성은 챙기지만 코스트가 좀 있음.
    comment_count: int = 0 # 정식 경로로 삭제된게 아닌 cascade로 삭제되면 데이터 무결성이 깨짐. 계속 추적하면 무결성은 챙기지만 코스트가 좀 있음.


class User_Read(User_Base):
    pass


class User(User_Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    posts: list["Post"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "delete"})
    comments: list["Comment"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "delete"})


