"""
original geocoding module

.. autosummary::
    :toctree:

    __main__
    activate_reverse
    ban_processing
    datapaths
    datatypes
    distance
    download
    index
    normalize
    query
    result
    search
    similarity
    utils
"""
import os
import boto3

try:
    DEBUG = (os.getenv("DEBUG", 'False').lower() in ('true', '1', 't'))
    LOCAL_DB = (os.getenv("LOCAL_DB", 'True').lower() in ('true', '1', 't'))
except ValueError:  # pragma: no cover
    DEBUG = False
    LOCAL_DB = True

if DEBUG and not os.environ.get("LOGURU_LEVEL"):
    os.environ["LOGURU_LEVEL"] = "DEBUG"
elif not os.environ.get("LOGURU_LEVEL"):  # pragma: no cover
    os.environ["LOGURU_LEVEL"] = "ERROR"

if not LOCAL_DB:
    s3 = boto3.client('s3',
                      endpoint_url=os.environ.get("S3_ENDPOINT_URL"),
                      use_ssl=True,
                      verify=False)
else:
    s3 = None
