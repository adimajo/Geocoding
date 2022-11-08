ARG DOCKER_REGISTRY
FROM ${DOCKER_REGISTRY}python:3.8.13-alpine3.16 as build
COPY geocoder geocoder/
COPY README.rst README.rst
COPY setup.py setup.py
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apk --update add --no-cache git openblas-dev linux-headers build-base &&\
    pip install --upgrade pip &&\
    pip install pipenv &&\
    pipenv install --system --deploy &&\
    touch requirements.txt && python3 -m pip install .
RUN chown nobody:nogroup /geocoder &&\
    chmod +x geocoder &&\
    geocoder download &&\
    geocoder decompress &&\
    geocoder index &&\
    geocoder reverse &&\
    geocoder clean

FROM ${DOCKER_REGISTRY}python:3.8.13-alpine3.16 as run

COPY --from=build /usr /usr

EXPOSE 8000
USER nobody
ENTRYPOINT geocoder runserver
