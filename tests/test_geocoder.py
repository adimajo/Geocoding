import json
import shutil
import sys

import pytest

import geocoder
from geocoder import __version__
from geocoder.geocoding.activate_reverse import create_kdtree
from geocoder.geocoding.datapaths import database
from geocoder.geocoding.download import check_ban_version, decompress, remove_downloaded_raw_ban_files
from geocoder.geocoding.index import process_files, create_database
from geocoder.wsgi import app

check_ban_version()
check_ban_version()  # to test "no need to download"
decompress()
process_files()
create_database()
create_kdtree()
remove_downloaded_raw_ban_files()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = "TEST"

    with app.test_client() as client:
        yield client


def test_version(client, caplog):
    response = client.get('/version')
    assert json.loads(response.data.decode("utf-8"))["version"] == __version__


def test_geocode(client, caplog):
    response = client.get('/geocode/Rue+du+Professeur+Christian+Cabrol/01500/Ambérieu-en-Bugey')
    assert round(json.loads(response.data.decode("utf-8"))["data"][0]["lon"], 2) == 4.94
    assert round(json.loads(response.data.decode("utf-8"))["data"][0]["lat"], 2) == 45.93
    response = client.get('/')
    response = client.get('/use')


def test_geocode_file(client, caplog):
    json_file = json.dumps([{
        'address': "Rue du Professeur Christian Cabrol",
        'postal_code': "01500",
        'city': "Ambérieux-en-Bugey"}])
    response = client.post('/geocode_file', json=json_file)
    assert round(json.loads(response.data.decode("utf-8"))["data"][0]["lon"], 2) == 4.94
    assert round(json.loads(response.data.decode("utf-8"))["data"][0]["lat"], 2) == 45.98


def test_functions():
    output = geocoder.find('01500', 'Ambérieu-en-Bugey', 'Rue du Professeur Christian Cabrol')
    assert round(output['longitude'], 2) == 5.35
    assert round(output['latitude'], 2) == 45.98

    output = geocoder.find('01400', None, '630, la Chèvre')
    assert round(output['longitude'], 2) == 4.91
    assert round(output['latitude'], 2) == 46.13

    query = (2.2099, 48.7099)
    output = geocoder.near(query)
    assert output['commune']['nom'] == "SERMOYER"  # should be "PALAISEAU" with full DB
    assert output['voie']['nom'] == "CORNE DE VACHON"  # should be "BOULEVARD DES MARECHAUX" with full DB


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    if 'geocoder' in sys.modules:
        del sys.modules["geocoder"]
    shutil.rmtree(database)
