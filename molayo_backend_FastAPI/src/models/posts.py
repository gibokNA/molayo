from typing import Optional, TYPE_CHECKING
from sqlmodel import JSON, SQLModel, Field, Column, Relationship

if TYPE_CHECKING:
    from .users import User


class Post_Base(SQLModel):
    title: str = Field(index=True)
    body: str


class Post_Create(Post_Base):
    pass


class Post_Update(Post_Base):
    pass


class Post(Post_Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str = Field(index=True)

    created: Optional[str] = None
    edited: Optional[str] = None

    likes: list[str] = Field(default=[], sa_column=Column(JSON)) # 이거 뭔가 작동안하는듯. 애초에 sqlite가 json 지원안하나? django에서는 됬었는데. 뭔가 지원안하나보네. postgre로 옮기기
    comments: list["Comment"] = Relationship(sa_relationship_kwargs={"cascade": "delete"}, back_populates="post")

    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0 # 정식 경로로 삭제된게 아닌 cascade로 삭제되면 데이터 무결성이 깨짐. 계속 추적하면 무결성은 챙기지만 코스트가 좀 있음.

    username: str = Field(foreign_key="user.username")
    user: "User" = Relationship(back_populates="posts")
    

class Comment_Base_1(SQLModel):
    text: str


class Comment_Create(Comment_Base_1):
    pass


class Comment_Base_2(Comment_Base_1):
    id: int
    username: str
    nickname: str
    post_id: int = Field(foreign_key="post.id")
    created: str


class Comment_Read(SQLModel):
    comments: list[Comment_Base_2]
    comment_count: int


class Comment(Comment_Base_2, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    post: Post = Relationship(back_populates="comments")

    username: str = Field(foreign_key="user.username")
    user: "User" = Relationship(back_populates="comments")


class Post_Read_Base(SQLModel):
    id: int
    username: str
    nickname: str
    title: str
    created: str
    edited: Optional[str] = None

    view_count: int
    like_count: int
    comment_count: int


class Post_List_Read(Post_Read_Base):
    pass


class Post_Read(Post_Read_Base):
    body: str
    comments: list[Comment]


