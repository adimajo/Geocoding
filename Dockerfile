ARG DOCKER_REGISTRY
ARG BASE_IMAGE
FROM ${DOCKER_REGISTRY}${BASE_IMAGE}
ARG EMAIL
ARG APPLICATION_TAG_VERSION
ENV EMAIL ${EMAIL}
ENV APPLICATION_TAG_VERSION ${APPLICATION_TAG_VERSION}
COPY geocoder geocoder/
COPY README.md setup.py Pipfile Pipfile.lock ./

RUN apk --update add --no-cache git openblas-dev linux-headers build-base || true &&\
    pip install --upgrade pip &&\
    pip install pipenv
RUN pipenv install --categories "packages api" --system --deploy &&\
    python3 -m pip install .
RUN chmod +x geocoder &&\
    chown -R nobody:nogroup /usr/local/lib/python3.8/site-packages/ &&\
    rm -rf geocoder &&\
    rm -f README.md Pipfile Pipfile.lock setup.py

LABEL da.da/geocoder.version=$APPLICATION_TAG_VERSION \
      da.da/geocoder.contact=$EMAIL

USER nobody

ENTRYPOINT geocoder update &&\
    geocoder runserver
