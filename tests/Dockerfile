# run from repo root for repeatable tests
# docker build -f tests/Dockerfile . --progress plain --no-cache
FROM python:3.8-alpine
WORKDIR /project
COPY . .
RUN pip install -e .[dev]
RUN pytest
