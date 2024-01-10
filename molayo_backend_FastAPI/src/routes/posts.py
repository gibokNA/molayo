from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, Body, Path, Query, UploadFile
from sqlmodel import select, or_
from connection import get_session
from routes.users import get_user
import time

from models.posts import Post, Post_Create, Post_Update, Comment, Comment_Create, Comment_Read, Post_Read, Post_List_Read
from models.users import User

import uuid, aiofiles

posts_router = APIRouter()

####################################################################
# 경로 매칭


@posts_router.post("")
async def create_post(
        body_data: Annotated[Post_Create, Body()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_session)
    ):
    
    if len(body_data.title) == 0 or len(body_data.body) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="제목 or 내용 없음.",
        )

    post = Post(nickname=user.nickname, title=body_data.title, body=body_data.body, created=str(time.time()), user=user, username=user.username)
    user.post_count += 1

    session.add(user)
    session.add(post)
    session.commit()

    return post.id

@posts_router.get("/search", response_model=list[Post_List_Read])
async def search_posts(
        q: Annotated[str , Query()],
        target: Annotated[str, Query(description="all, nickname, title 3가지 중 하나 선택하세요.")] = "all",
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=50)] = 50,
        session=Depends(get_session)
    ):

    statement = select(Post).order_by(Post.id.desc())

    print(target)

    if target == "all":
        statement = statement.where(or_(Post.nickname.contains(q), Post.title.contains(q)))
    elif target == "nickname":
        statement = statement.where(Post.nickname.contains(q))
    elif target == "title":
        statement = statement.where(Post.title.contains(q))

    statement = statement.offset(offset).limit(limit)

    searched_data = session.exec(statement).all()

    return searched_data


@posts_router.get("/{post_id}", response_model=Post_Read)
async def read_post(
        post_id: Annotated[int, Path()],
        session=Depends(get_session)
    ):

    post = get_post(post_id, session)

    post.view_count += 1
    session.add(post)
    session.commit()
    session.refresh(post)

    post_dict = post.model_dump()

    try:
        post.comments.reverse()
        post_dict["comments"] = post.comments[0:50]
    except:
        post_dict["comments"] = []

    return Post_Read(**post_dict)


@posts_router.get("", response_model=list[Post_List_Read])
async def read_post_list(
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=50)] = 50,
        session=Depends(get_session)
    ):

    statement = select(Post).order_by(Post.id.desc()).offset(offset).limit(limit)
    post_list = session.exec(statement).all()

    return post_list


@posts_router.put("/{post_id}")
async def edit_post(
        post_id: Annotated[int, Path()],
        body_data: Annotated[Post_Update, Body()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_session)
    ):

    if len(body_data.title) == 0 or len(body_data.body) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    post = get_post(post_id, session)
    
    if post.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    post.title = body_data.title
    post.body = body_data.body
    post.edited = str(time.time())
    
    session.add(post)
    session.commit()

    return True


@posts_router.delete("/{post_id}")
async def delete_post(
        post_id: Annotated[int, Path()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_session)
    ):

    post = get_post(post_id, session)
    
    if post.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user.post_count -= 1

    session.add(user)
    session.delete(post)
    session.commit()

    return True


@posts_router.get("/{post_id}/like")
async def submit_like(
        post_id: Annotated[int, Path()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_session)
    ):

    # 이거 sqlite에서 작동안함. postgre에서 테스트해봐야함.

    post = get_post(post_id, session)

    print("user.username : ", user.username)
    print("post.likes : ", post.likes)

    if user.username in post.likes:
        print(1)
        del post.likes[post.likes.index(user.username)]
        post.like_count -= 1
    else:
        print(2)
        post.likes.append(user.username)
        post.like_count += 1

    print(post.likes)

    session.add(post)
    session.commit()

    return True


@posts_router.post("/{post_id}/comments")
async def create_comment(
        post_id: Annotated[int, Path()],
        data: Annotated[Comment_Create, Body()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_session)
    ):

    if len(data.text) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    post = get_post(post_id, session)
    
    comment = Comment(post_id=post_id, nickname=user.nickname, username=user.username, created=str(time.time()), text=data.text)

    post.comment_count += 1
    user.comment_count += 1

    session.add(user)
    session.add(post)
    session.add(comment)
    session.commit()
    
    return True


@posts_router.get("/{post_id}/comments", response_model=Comment_Read)
async def read_comments(
        post_id: Annotated[int, Path()],
        offset: Annotated[int, Query(ge=0)] = 50,
        limit: Annotated[int, Query(gt=0, le=50)] = 50,
        session=Depends(get_session)
    ) -> list[Comment]:

    post = get_post(post_id, session)

    try:
        post.comments.reverse()
        comments = post.comments[offset:(offset+limit)]
    except:
        comments = []

    return_dict = {
        "comments": comments,
        "comment_count": post.comment_count
    }

    return return_dict


@posts_router.delete("/{post_id}/{comment_id}")
async def delete_comment(
        post_id: Annotated[int, Path()],
        comment_id: Annotated[int, Path()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_session)
    ):

    post = get_post(post_id, session)
    
    comment = session.get(Comment, comment_id)

    if comment == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if comment.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    post.comment_count -= 1
    user.comment_count -= 1

    session.add(post)
    session.add(user)
    session.delete(comment)
    session.commit()

    return True


@posts_router.post('/upload-image')
async def upload_image(
        file: UploadFile,
        user: Annotated[User, Depends(get_user)],
    ):

    local_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="허가되지 않은 이미지 포맷"
    )

    if not file.filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'gif', 'png', 'webp', 'bmp']:
        raise local_exception
    
    if not 'image' in file.content_type:
        raise local_exception
    
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="사이즈가 너무 큼. 최대 10mb 까지만 허용."
        )
    
    file_name = str(uuid.uuid1().hex) + '.' + file.filename.split('.')[-1]
    file_path = '/usr/share/nginx/html/static/' + file_name

    async with aiofiles.open(file_path, 'wb') as f:
        while chunked_data := await file.read(1024):
            await f.write(chunked_data)

    file_path = "https://molayo.work/static/" + file_name # 이거 배포할때 경로변경해줘야함.

    return {"url": file_path}

####################################################################

def get_post(post_id: int, session):
    post = session.get(Post, post_id)

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return post

####################################################################