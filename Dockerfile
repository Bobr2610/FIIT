# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /fiit

RUN apt update && \
    apt install dos2unix

RUN pip install --upgrade pip && \
    pip install poetry

COPY pyproject.toml .

RUN poetry config virtualenvs.create false &&  \
    poetry install

COPY . .

RUN find -type f -name "*.sh" -exec dos2unix {} \;

EXPOSE 8000

CMD sh scripts/backend/start.sh
