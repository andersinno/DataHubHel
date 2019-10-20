FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -U pip \
    && pip install -r requirements.txt
