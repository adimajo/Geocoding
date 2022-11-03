ARG DOCKER_REGISTRY
FROM ${DOCKER_REGISTRY}python:3.8.13-alpine3.16 as build
ENV PIPENV_PIPFILE geocoder/Pipfile
COPY geocoder geocoder/
COPY README.rst README.rst
COPY setup.py setup.py

RUN apk --update add --no-cache git openblas-dev linux-headers build-base &&\
    pip install --upgrade pip &&\
    pip install pipenv &&\
    PIPENV_PIPFILE=geocoder/Pipfile pipenv install --system --deploy &&\
    touch requirements.txt && python3 -m pip install .
RUN chown nobody:nogroup /geocoder &&\
    geocoder download &&\
    geocoder decompress &&\
    geocoder index &&\
    geocoder reverse &&\
    geocoder clean

EXPOSE 8000
USER nobody
ENTRYPOINT gunicorn geocoder.wsgi:app --bind 0.0.0.0:8000
