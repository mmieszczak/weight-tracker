ARG PYTHON_VERSION=3.10
ARG ALPINE_VERSION=3.17
ARG BASE_IMAGE=python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

# Build stage
FROM ${BASE_IMAGE} AS build-stage

# Install build dependencies
RUN apk add --no-cache poetry

# Install python dependencies into /install prefix
WORKDIR /src
COPY pyproject.toml poetry.lock /src/
RUN poetry env use /usr/local/bin/python && \
	poetry export | pip install --prefix /install --requirement /dev/stdin

# Install python application into /install prefix
COPY . /src/
RUN poetry build && pip install --prefix /install dist/*.whl

# Run stage
FROM ${BASE_IMAGE}

# Copy application from build stage to run stage
COPY --from=build-stage /install /usr/local

ENTRYPOINT [ "weight-tracker" ]
EXPOSE 8080
