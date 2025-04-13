# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /fiit

COPY . .

RUN pip install --upgrade pip &&  \
    pip install poetry &&  \
    poetry config virtualenvs.create false &&  \
    poetry install

EXPOSE 8000

CMD python backend/manage.py makemigrations &&  \
    python backend/manage.py migrate &&  \
    python backend/manage.py runserver 0.0.0.0:8000
