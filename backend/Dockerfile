FROM python:3.10-slim-buster
WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY common ./common
COPY orders_service ./orders_service

COPY main.py .