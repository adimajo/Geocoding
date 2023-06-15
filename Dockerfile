ARG DOCKER_REGISTRY
ARG BASE_IMAGE
FROM ${DOCKER_REGISTRY}${BASE_IMAGE}
ARG EMAIL
ARG APPLICATION_TAG_VERSION
ENV EMAIL ${EMAIL}
ENV APPLICATION_TAG_VERSION ${APPLICATION_TAG_VERSION}
COPY geocoder geocoder/
COPY README.md README.md
COPY setup.py setup.py
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apk --update add --no-cache git openblas-dev linux-headers build-base || true &&\
    pip install --upgrade pip &&\
    pip install pipenv
RUN pipenv install --categories "packages api" --system --deploy &&\
    python3 -m pip install .
RUN chown nobody:nogroup /geocoder &&\
    chmod +x geocoder

LABEL da.da/geocoder.version=$APPLICATION_TAG_VERSION \
      da.da/geocoder.contact=$EMAIL

RUN rm -rf geocoder && rm -f README.md Pipfile Pipfile.lock setup.py
ENTRYPOINT geocoder update &&\
    geocoder runserver
