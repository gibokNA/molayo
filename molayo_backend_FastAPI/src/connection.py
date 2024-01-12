"""
개발단계에서 sqlite 쓸때의 코드

from sqlmodel import SQLModel, Session, create_engine

database_file = "/app/data/database.db"
database_connection_string = f"sqlite:///{database_file}"
connect_args = {"check_same_thread": False}
engine_url = create_engine(database_connection_string, echo=False, connect_args=connect_args)

def conn():
    SQLModel.metadata.create_all(engine_url)

def get_session():
    with Session(engine_url) as session:
        yield session
"""

import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

DATABASE_URL = os.environ.get("DATABASE_URL")

async_engine = create_async_engine(
   DATABASE_URL,
   echo=False,
   future=True
)

"""
async def init_db():
    async with async_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
"""
        
async def get_async_session() -> AsyncSession:
   async_session = sessionmaker(
       bind=async_engine, class_=AsyncSession, expire_on_commit=False
   )
   async with async_session() as session:
       yield session



"""
alembic 은 데이터 베이스 마이그레이션 라이브러리. ORM을 사용하기 때문에 사용해야함.
python code <-> ORM <-> postgres

백엔드 모델 클래스와 실제 DB의 테이블이 서로 다르기 때문에 깃으로 코드 갱신하듯이
파이썬코드에서 이전코드와 현재의 변경사항을 추적한뒤 실제 DB에 반영.

django에서 했던 makemigrations, migrate 와 똑같음.
makemigration은 DB에 반영할 변경사항을 먼저 만들어놓는것. 아직 실제 반영 X
migrate는 makemigration으로 만들어진 migration 파일을 참조해서 실제 DB에 반영.

실제 운영상태가 아닌 개발초기에는 필요가 없음. 테스트 할때마다 매번 DB 지우고 새로 만들고 하면 되니까.
그런데 실제 운영중일때는 이렇게 DB를 막 지울수가 없음. 그래서 실제 DB의 현재 상태와 추가할 코드, 변경사항을
비교해서 반영한다음 기록을 남기는거지.

요즘 배포는 대부분 도커로 이루어짐. postgres도 도커 컨테이너로 실행되는데 문제가 컨테이너는 껏다 킬때마다 데이터유지가 안됨.
컨테이너를 시작하면 초기에 사용한 이미지 그대로 만들어짐. 데이터 유지 X. 그래서 docker-compose volume으로 데이터를 유지함.
실제 데이터는 volume 안에서 유지가 되고...

그래서 마이그레이션 작업은 container bash 로 해야 실제로 의미가 있을듯??
흠........................................................
로컬 개발환경에서 마이그레이션해봤자 의미가 있나?
아니면 운영환경과 개발환경에서의 DB를 똑같이 유지하고.. 즉 볼륨을 계속 유지한다음
마이그레이션 하고 migrations 폴더 자체를 이미지에 포함시킨뒤 docker-compose에서 시작할떄 마이그레이션 자동화 하기?
일단 해봐야할듯. 아직 감이 안잡히는데.

아 지금 서버하나에 nginx, fastapi, DB가 전부 들어가 있어서 docker-compose로 할수 있는데
어차피 fastapi와 DB가 다른서버에 있으면 docker-compose로는 안될듯? 그러면 container bash를 통해서 수동으로 해주거나 해야할텐데.

아니면 쿠버네티스에서 이 프로세스를 자동화 해주는 뭔가가 있을지도??

# https://testdriven.io/blog/fastapi-sqlmodel/

docker-compose exec molayo-backend poetry run alembic init -t async migrations   맨 처음에 alembic 초기화

script.py.mako 안에서 
import sqlmodel

env.py 안에서 
from sqlmodel import SQLModel
from models.users import User
from models.posts import Post, Comment
target_metadata = SQLModel.metadata

alembic.ini 안에서
sqlalchemy.url = 이거 환경변수에 저장된 dburl 가져오기.

docker-compose exec molayo-backend poetry run alembic revision --autogenerate -m "init"
이러면 src/migrations/versions 안에 마이그레이션 파일이 만들어짐.

docker-compose exec molayo-backend poetry run alembic upgrade head   이렇게하면 마이그레이션 파일 참조해서 실제 DB에 반영.

모델에 필드 추가한뒤
docker-compose exec molayo-backend poetry run alembic revision --autogenerate -m "temp_field" 요렇게 하면 
모델에 새로 추가한 필드의 변경사항이 마이그레이션 파일로 만들어짐.

docker-compose exec molayo-backend poetry run alembic upgrade head   실제 DB에 반영

이제 docker-compose down으로 컨테이너 내렸다가 docker-compose up -d 로 다시 올리면
migrations 폴더랑 여러가지가 초기화 됬음.

postgres 는 molayo-db-volume:/var/lib/postgresql/data 으로 이전 변경사항과 데이터 유지중...
이미지 안에 개발단계에서 사용한 migration 폴더와 등등을 포함시켜놓고
처음에 도커 허브에서 최신 이미지 받아올때 첫번쨰에 수동으로 마이그레이션 해주기.
entrypoint나 command로 마이그레이션 자동화하면 매번 on/off 마다 계속 중복되지 않을까??

일단 이미지에 포함까지만 시키고 수동으로 해보자.


***총정리***

개발환경에서 로컬DB를 통해 migrations/versions 폴더를 갱신함.
도커 이미지를 만들때 migrations/versions 까지 포함시켜서 만들고 docker-compose로 컨테이너를 실행시킬때
poetry run alembic upgrade head 이 명령어로 업데이트 자동화 시키기.
migrations/versions 에서 변화가 없으면 alembic upgrade head 실행해도 변화없음. 즉 중복 없음. 자동화 가능

로컬 개발환경에서 migration 파일을 만들때 db_url의 호스트를 localhost로 변경한뒤 실행해야함.
운영환경에서는 컨테이너의 이름이 호스트 이름이기 때문에 molayo-db 로 변경한뒤 실행.

alembic.ini 안에 db_url 하드코딩하지 말고 환경변수로 빼준뒤 env.py 에서 주입해주기.

로컬DB를 항상 유지할 필요없음. migrations/versions 폴더에 v1, v2, v3 ... 이렇게 마이그레이션 버전 파일들이 존재할때,
새로만든 로컬DB에 마이그레이션 한번 해주면 v1, v2, v3... 전부 적용되서 최신상태로 유지됨.




"""