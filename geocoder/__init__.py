"""
geocoder modules and API

.. autosummary::
    :toctree:

    api
    geocoding
    wsgi
"""
from loguru import logger
from geocoder.geocoding import search, query

__version__ = "2.1.13"

find = search.position
near = search.reverse

logger.info('Loading geocoding data')
query.setup()
