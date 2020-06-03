#!/bin/sh
docker stop cards-test
docker rm cards-test
docker build -t cards-fastapi . &&
    docker run --name cards-test -p 80:80 cards-fastapi
