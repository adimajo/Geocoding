ARG DOCKER_REGISTRY
FROM python:3.8-slim as build

ENV PIPENV_PIPFILE geocoding/Pipfile

COPY . geocoding/

EXPOSE 8000

RUN pip install --upgrade pip && pip install pipenv
RUN pipenv install --system --deploy
RUN chown nobody:nogroup /geocoding

COPY geocoding ./geocoding
COPY requirements.txt .
COPY README.rst .
COPY version.txt .
COPY setup.py .

RUN geocoding download
RUN geocoding decompress
RUN geocoding index
RUN geocoding remove_non_necessary_files

FROM python:3.8-slim as run

COPY --from=build $WORKING_DIR/README.rst $WORKING_DIR

COPY api ./api
COPY site ./site
COPY run.py .
COPY LICENSE .

ARG appPort
RUN echo "PORT = ${appPort}" > api/port.py
EXPOSE ${appPort}

USER nobody

ENTRYPOINT gunicorn whiteapp.wsgi:app --bind 0.0.0.0:8000
