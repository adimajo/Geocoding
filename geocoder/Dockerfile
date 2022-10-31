ARG DOCKER_REGISTRY
FROM ${DOCKER_REGISTRY}python:3.8.13-alpine3.16 as build
ENV PIPENV_PIPFILE geocoder/Pipfile
COPY . geocoder/

RUN apk --update add --no-cache git openblas-dev linux-headers build-base
RUN pip install --upgrade pip && pip install pipenv
RUN PIPENV_PIPFILE=geocoder/Pipfile pipenv install --system --deploy
RUN chown nobody:nogroup /geocoder
RUN geocoder download
RUN geocoder decompress
RUN geocoder index
RUN geocoder reverse
RUN geocoder clean

EXPOSE 8000
USER nobody
ENTRYPOINT gunicorn geocoder.wsgi:app --bind 0.0.0.0:8000
