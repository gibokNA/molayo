FROM python:3.10.10-slim

RUN apt-get update && apt-get install -y build-essential

WORKDIR /app
COPY . /app

RUN pip install poetry

RUN poetry install

WORKDIR /app/src