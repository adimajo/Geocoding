import json
import shutil
import sys

import pytest

import geocoder
from geocoder import __version__
from geocoder.geocoding.activate_reverse import create_kdtree
from geocoder.geocoding.datapaths import database
from geocoder.geocoding.download import get_ban_file, decompress, remove_downloaded_raw_ban_files
from geocoder.geocoding.index import process_files, create_database
from geocoder.wsgi import app

get_ban_file()
get_ban_file()  # to test "no need to download"
decompress()
process_files()
create_database()
create_kdtree()
remove_downloaded_raw_ban_files()


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_version(client, caplog):
    response = client.get('/version')
    assert json.loads(response.data.decode("utf-8"))["version"] == __version__


def test_geocode(client, caplog):
    response = client.get('/geocode/Rue+du+Professeur+Christian+Cabrol/01500/Ambérieu-en-Bugey')
    assert round(json.loads(response.data.decode("utf-8"))["data"][0]["lon"], 2) == 5.35
    assert round(json.loads(response.data.decode("utf-8"))["data"][0]["lat"], 2) == 45.93
    response = client.get('/')
    response = client.get('/use')


def test_functions():
    output = geocoder.find('01500', 'Ambérieu-en-Bugey', 'Rue du Professeur Christian Cabrol')
    assert round(output['longitude'], 2) == 5.35
    assert round(output['latitude'], 2) == 45.98

    output = geocoder.find('01400', None, '630, la Chèvre')
    assert round(output['longitude'], 2) == 4.91
    assert round(output['latitude'], 2) == 46.13

    query = (2.2099, 48.7099)
    output = geocoder.near(query)
    assert output['commune']['nom'] == "SERMOYER"
    assert output['voie']['nom'] == "ROUTE DE CUISERY"


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    if 'geocoder' in sys.modules:
        del sys.modules["geocoder"]
    shutil.rmtree(database)
