FROM python:alpine
RUN apk add --no-cache poetry
COPY . /src
WORKDIR /src
RUN poetry build && python -m pip install dist/*.whl
