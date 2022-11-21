ARG DOCKER_REGISTRY
ARG BASE_IMAGE
FROM ${DOCKER_REGISTRY}${BASE_IMAGE}
COPY geocoder geocoder/
COPY README.md README.md
COPY setup.py setup.py
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apk --update add --no-cache git openblas-dev linux-headers build-base || true &&\
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

RUN rm -rf geocoder && rm -f README.md Pipfile Pipfile.lock setup.py
ENTRYPOINT geocoder runserver
