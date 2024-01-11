FROM python:3.10.10-slim

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app
COPY . /app

RUN pip install poetry

RUN poetry install

WORKDIR /app/src

CMD ["poetry", "run", "gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
