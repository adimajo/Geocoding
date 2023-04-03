[![coverage report](https://gitlab.ca.cib/GIT/RCI/DA/geocoder/geocoder/badges/master/coverage.svg)](https://gitlab.ca.cib/GIT/RCI/DA/geocoder/geocoder/-/commits/master)
[![pipeline status](https://gitlab.ca.cib/GIT/RCI/DA/geocoder/geocoder/badges/master/pipeline.svg)](https://gitlab.ca.cib/GIT/RCI/DA/geocoder/geocoder/-/commits/master)
[![Python Flask app](https://github.com/adimajo/geocoder/actions/workflows/python-flask.yml/badge.svg?branch=master)](https://github.com/adimajo/geocoder/actions/workflows/python-flask.yml)

Geocoder
========

Geocoder is an address search engine for France.
Unlike other APIs, it uses a database provided by the 
rench government
(Base Adresse Nationale - BAN) as the main source of information and does
not impose any limit to the number of queries. The purpose of the project
is to supply the needs of french data scientists that rely on geocoded data.

Fork from [chrlryo/Geocoding](https://github.com/chrlryo/Geocoding) itself
a fork from [DeVilhena-Paulo/Geocoding](https://github.com/DeVilhena-Paulo/Geocoding).


Getting Started
===============

Prerequisites
-------------

* Python version 3 installed locally
* Pipenv installed locally
* Docker (for geocoding API use)

Using API with Docker
---------------------

Build the API server locally

```shell
docker build --build-arg app_port=8088 --progress=plain -t geocoding-api .
```

Docker requirements for building

* Memory 12Gb
* Disk image size 50Gb

Use it

```shell
docker run -p 8000:8000 geocoding-api
```
The API is available through:

* In your browser:

  * http://localhost:8000
  * http://localhost:8000/use
  * http://localhost:8000/geocode/<address>/<postal_code>/<city>

* With Curl:

```shell
curl --header "Content-Type: application/json" \
--request POST \
--data '[{"address": "...", "postal_code": "...", "city": "..."}, {"address": "...", "postal_code": "...", "city": "..."}]' \
http://localhost:8000/geocode_file
```

Example:

```shell
curl --header "Content-Type: application/json" \
--request POST \
--data '[{"address": "12, Bd des Maréchaux", "postal_code": "91120", "city": "Palaiseau"}]' \
http://localhost:8000/geocode_file
```

Using Python package
--------------------

The package can be installed via pip (only on Crédit Agricole's internal Artifactory repository):

```shell
pip install geocoder
```

The package can also be installed from Github:

```shell
pip install git+https://github.com/adimajo/geocoder.git
```

Before the first use, you need to download the BAN database and process its files to unlock the functionalities of the package. All of this can be done with the following command (the whole process should take 30 minutes)::

```shell
geocoder update
```

Alternatively, you can do it step by step with the following commands:

```shell
geocoder download
geocoder decompress
geocoder index
geocoder remove_non_necessary_files
```

To unlock the reverse search, execute the following command:

```shell
geocoder reverse
```

Usage
=====

The search engine
-----------------

```python
import geocoder


# -*- Complete search -*-
output = geocoder.find('91120', 'Palaiseau', '12, Bd des Maréchaux')
print(output['longitude'], output['latitude'])  # 2.2099342 48.7099138

# -*- Incomplete search -*-
output = geocoder.find('91120', None, '12, Bd des Maréchaux')
print(output['quality'])  # 1 -> It means that the search was successful

output = geocoder.find('91120', None, 'Bd des Maréchaux')
print(output['quality'])  # 3 -> It means that the number was not found

output = geocoder.find('91120', 'Palaiseau', None)
print(output['quality'])  # 4 -> It means that the street was not found

output = geocoder.find(None, 'Palaiseau', '12, Bd des Maréchaux')
print(output['quality'])  # 1

output = geocoder.find(None, None, '12, Bd des Maréchaux')
print(output['postal']['code'])  # 35800
print(output['commune']['nom'])  # DINARD
print(output['voie']['nom'])  # BOULEVARD DES MARECHAUX

# -*- Search with typos -*-
geocoder.find('91120', 'Palaiseau', '12, Bd des Maréchx')['quality']  # 1
geocoder.find('91120', 'Palaiau', '12, Bd des Maréchx')['quality']  # 1
geocoder.find('91189', 'Palaiseau', '12, Bd des Maréchx')['quality']  # 1
geocoder.find('91189', None, '12, Bd des Maréchx')['quality']  # 1

# -*- Flexible syntax -*-
geocoder.find('91120', 'Palaiseau')['quality']  # 4
geocoder.find(commune='Palaiseau')['quality']  # 4
geocoder.find('91120')['quality']  # 5

args = {
    'code_postal': '91120',
    'commune': 'Palaiseau',
    'adresse': '12, Bd Marechaux'
}
geocoder.find(**args)
```

The reverse functionality
-------------------------

```python
import geocoder

# longitude and latitude
query = (2.2099, 48.7099)
output = geocoder.near(query)
output['commune']['nom']  # PALAISEAU
output['voie']['nom']  # BOULEVARD DES MARECHAUX
```

Benchmarks
----------

```python
import time
import geocoder

begin = time.time()
for _ in range(2000):
    geocoder.find('91130', 'PALISEAU', '12 BD DES MARECHUX')
print(time.time() - begin, 'seconds')  # 1.063 seconds

begin = time.time()
for _ in range(10000):
    geocoder.find('91120', 'PALAISEAU', '12 BD DES MARECHAUX')
print(time.time() - begin, 'seconds')  # 1.407 seconds

begin = time.time()
for _ in range(10000):
    geocoder.find('75015', 'PARIS', '1 RUE SAINT CHARLES')
print(time.time() - begin, 'seconds')  # 1.525 seconds

begin = time.time()
for _ in range(1000):
    geocoder.near((2, 48))
print(time.time() - begin, 'seconds')  # 0.922 seconds
```
