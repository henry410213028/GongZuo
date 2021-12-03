FROM python:3.8-slim-buster

RUN apt-get update

RUN mkdir /project
COPY . /project/
WORKDIR /project/

RUN pip install pipenv && pipenv sync