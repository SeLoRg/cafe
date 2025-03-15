FROM python:3.10-slim-buster
WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt ./alembic_service/requirements.txt
RUN pip install -r ./alembic_service/requirements.txt

COPY common ./common
COPY alembic_service ./alembic_service

WORKDIR /app/alembic_service