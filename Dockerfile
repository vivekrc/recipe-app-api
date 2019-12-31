FROM python:3.7-alpine
MAINTAINER vivek at tessel dot tech

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# this is for the security. Hacker does not get access to root directly
RUN adduser -D user
USER user
