ARG DOCKER_REGISTRY
ARG EMAIL
ARG BASE_IMAGE

FROM ${DOCKER_REGISTRY}${BASE_IMAGE}
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

RUN LOGURU_LEVEL="ERROR" python3 -c 'import geocoder; print(geocoder.__version__)'  # otherwise next line doesn't error
RUN LOGURU_LEVEL="ERROR" export APPLICATION_TAG_VERSION=`python3 -c 'import geocoder; print(geocoder.__version__)'`

LABEL da.da/geocoder.version=$APPLICATION_TAG_VERSION \
      da.da/geocoder.contact=$EMAIL

RUN rm -rf geocoder && rm -f README.md Pipfile Pipfile.lock setup.py
ENTRYPOINT geocoder update &&\
    geocoder runserver
