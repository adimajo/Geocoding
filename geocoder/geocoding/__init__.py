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

try:
    DEBUG = (os.getenv("DEBUG", 'False').lower() in ('true', '1', 't'))
except ValueError:  # pragma: no cover
    DEBUG = False

if DEBUG and not os.environ.get("LOGURU_LEVEL"):
    os.environ["LOGURU_LEVEL"] = "DEBUG"
elif not os.environ.get("LOGURU_LEVEL"):  # pragma: no cover
    os.environ["LOGURU_LEVEL"] = "ERROR"
