from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, Form, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from password_validator import PasswordValidator
from sqlmodel import select
from connection import get_async_session
import time, os
from models.users import User, Token, User_Read
from models.posts import Post_List_Read, Comment

from sqlalchemy.orm import selectinload

# to get a string like this run:
# openssl rand -hex 32

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

password_scheme = PasswordValidator()
password_scheme\
.min(8)\
.max(100)\
.has().digits()\
.has().no().spaces()\

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

users_router = APIRouter()

##################################################################################
# method


# 여기는 토큰받아서 그 토큰에 맞는 유저 정보를 리턴하기.
async def get_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session=Depends(get_async_session)
    ): 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        statement = select(User).where(User.username == username).options(selectinload(User.posts)).options(selectinload(User.comments))
        result = await session.exec(statement)
        user = result.one()

        return user

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

###################################################################################
# 경로 매칭

# 회원가입
@users_router.post("")
async def user_register(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        password2: Annotated[str, Form()],
        nickname: Annotated[str, Form()],
        session=Depends(get_async_session)
    ):

    statement = select(User.username)
    result = await session.exec(statement)
    all_username_list = result.all()

    if form_data.username in all_username_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username aleady exists."
        )

    if form_data.password != password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password1 != password2"
        )
    
    if password_scheme.validate(form_data.password) == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 8자 이상, 100자 이하, 문자, 숫자를 포함해야하고 공백이 없어야함."
        )

    user_dict = {
        "username": form_data.username,
        "nickname": nickname,
        "hashed_password": pwd_context.hash(form_data.password),
        "posts": []
    }

    user = User(**user_dict)

    session.add(user)
    await session.commit()

    return True

# 토큰 반환
@users_router.post("/token", response_model=Token)
async def user_login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session=Depends(get_async_session)
    ):
    local_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    statement = select(User.hashed_password).where(User.username == form_data.username)

    try:
        result = await session.exec(statement)
        hashed_password = result.one()
    except:
        raise local_exception

    if pwd_context.verify(form_data.password, hashed_password) == False:
        raise local_exception
    
    expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    to_encode = {
        "sub": form_data.username,
        "exp": expire
    }

    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}

# 개인정보 불러오기
@users_router.get("/me", response_model=User_Read)
async def get_user_info(user: Annotated[User, Depends(get_user)]):
    return user

# 비밀번호 변경
@users_router.put("/password")
async def change_user_password(
        user: Annotated[User, Depends(get_user)],
        old_password: Annotated[str, Form()],
        new_password: Annotated[str, Form()],
        session=Depends(get_async_session)
    ):
    
    if pwd_context.verify(old_password, user.hashed_password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이전 비밀번호가 일치하지 않습니다."
        )
    
    if password_scheme.validate(new_password) == False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="비밀번호는 8자 이상, 100자 이하, 문자, 숫자를 포함해야하고 공백이 없어야함."
        )
    
    user.hashed_password = pwd_context.hash(new_password)

    session.add(user)
    await session.commit()

    return True

@users_router.put("/nickname")
async def change_nickname(
        new_nickname: Annotated[str, Body()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_async_session)
    ):

    user.nickname = new_nickname
    session.add(user)
    await session.commit()

    return True

# 계정삭제
@users_router.put("")
async def delete_user(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        user: Annotated[User, Depends(get_user)],
        session=Depends(get_async_session)
    ):
    local_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if form_data.username != user.username:
        raise local_exception

    if pwd_context.verify(form_data.password, user.hashed_password) == False:
        raise local_exception
    
    await session.delete(user)
    await session.commit()

    return True

# 계정의 게시글 목록 불러오기
@users_router.get("/posts", response_model=list[Post_List_Read])
async def get_user_posts(
        user: Annotated[User, Depends(get_user)],
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=50)] = 50,
    ):

    try:
        user.posts.reverse()
        posts = user.posts[offset:(offset+limit)]
    except:
        posts = []

    return posts

# 계정의 댓글 목록 불러오기
@users_router.get("/comments", response_model=list[Comment])
async def get_user_comments(
        user: Annotated[User, Depends(get_user)],
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(gt=0, le=50)] = 50,
    ):
    
    try:
        user.comments.reverse()
        comments = user.comments[offset:(offset+limit)]
    except:
        comments = []

    return comments