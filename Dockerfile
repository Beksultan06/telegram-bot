FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /temp/requirements.txt
COPY main /main

WORKDIR /main
EXPOSE 8000:8000

RUN apk add postgresql-client build-base postgresql-dev
RUN apk add --no-cache gcc musl-dev libffi-dev

RUN pip install --upgrade pip && pip install --upgrade setuptools
RUN pip install -r /temp/requirements.txt
