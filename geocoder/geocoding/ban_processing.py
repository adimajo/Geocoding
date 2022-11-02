"""
process decompressed files into a database

.. autosummary::
    test
    get_gield
    get_voie
    get_commune
    get_attributes
    update
    update_departement
    update_postal
    update_commune
    update_voie
    update_localisation
"""
# -*- coding: utf-8 -*-
import numpy as np
from sortedcontainers import SortedDict, SortedSet

from geocoder.geocoding import normalize as norm
from geocoder.geocoding.utils import degree_to_int

line_specs = {
    "adresses": {
        "nom_voie": 4,
        "numero": 2,
        "repetition": 3,
        "code_insee": 6,
        "code_postal": 5,
        "longitude": 12,
        "latitude": 13,
        "nom_commune": 7,
        "nom_complementaire": 16},
    "lieux-dits": {
        "nom_voie": None,
        "numero": None,
        "repetition": None,
        "code_insee": 3,
        "code_postal": 2,
        "longitude": 9,
        "latitude": 10,
        "nom_commune": 4,
        "nom_complementaire": None}
}

types = {
    "code_postal": int,
    "numero": int,
    "longitude": float,
    "latitude": float
}

voie_fields = ['nom_voie']

commune_fields = ['nom_complementaire', 'nom_commune']


def test(fields, lieu):
    for field in types:
        try:
            types[field](fields[line_specs[lieu][field]])
        except ValueError:
            return False
    return True


def get_field(field_name, fields, normalization_method, lieu, size_limit=None):
    field = line_specs[lieu][field_name]
    if field is None:  # pragma: no cover
        return None, None
    text = fields[field].replace('"', '')
    normalise = normalization_method(text)
    if len(normalise) > 0:
        nom = norm.remove_separators(norm.uniform(text))
        if size_limit is None or len(nom) <= size_limit:
            return nom, normalise
    return None, None


def get_voie(fields, lieu):
    for field_name in voie_fields:
        voie_nom, voie_normalise = get_field(field_name,
                                             fields,
                                             norm.uniform_adresse,
                                             lieu,
                                             47)
        if voie_nom is not None:
            return voie_nom, voie_normalise
    return None, None  # pragma: no cover


def get_commune(fields, lieu):
    for field_name in commune_fields:
        commune_nom, commune_normalise = get_field(field_name,
                                                   fields,
                                                   norm.uniform_commune,
                                                   lieu)
        if commune_nom is not None:
            return commune_nom, commune_normalise
    return None, None  # pragma: no cover


def get_attributes(fields, lieu: str = "adresses"):
    if not test(fields, lieu):
        return None  # pragma: no cover

    commune_nom, commune_normalise = get_commune(fields, lieu)
    if commune_nom is None:
        return None  # pragma: no cover

    voie_nom, voie_normalise = get_voie(fields, lieu)
    if voie_nom is None:
        return None  # pragma: no cover

    code_insee = fields[line_specs[lieu]['code_insee']]
    code_postal = int(fields[line_specs[lieu]['code_postal']])
    lon = degree_to_int(fields[line_specs[lieu]['longitude']])
    lat = degree_to_int(fields[line_specs[lieu]['latitude']])

    try:
        numero = int(fields[line_specs[lieu]['numero']])
        repetition = fields[line_specs[lieu]['repetition']].replace('"', '')
    except TypeError:  # pragma: no cover
        numero, repetition = None, None

    return (code_postal, commune_normalise, commune_nom, code_insee,
            voie_normalise, voie_nom, numero, repetition, lon, lat)


def update(dpt_nom, csv_file_path, processed_files):
    postal_dict = SortedDict()

    with open(csv_file_path, 'r', encoding='UTF-8') as f:
        next(f)
        for line in f:
            attributes = get_attributes(line.strip().split(';'))
            if attributes is None:
                continue
            postal_key = attributes[:1]
            commune_key = attributes[1:4]
            voie_key = attributes[4:6]
            localisation = attributes[6:]

            if postal_key not in postal_dict:
                postal_dict[postal_key] = SortedDict()

            commune_dict = postal_dict[postal_key]
            if commune_key not in commune_dict:
                commune_dict[commune_key] = SortedDict()

            voie_dict = commune_dict[commune_key]
            if voie_key not in voie_dict:
                voie_dict[voie_key] = SortedSet()

            voie_dict[voie_key].add(localisation)

    update_departement(dpt_nom, processed_files, postal_dict)


def update_departement(dpt_nom, processed_files, postal_dict):
    current_id = len(processed_files['departement'])

    start = len(processed_files['postal'])
    update_postal(current_id, processed_files, postal_dict)
    end = len(processed_files['postal'])

    processed_files['departement'].append((dpt_nom, start, end))


def update_postal(id_ref, processed_files, postal_dict):
    for key in postal_dict.keys():
        current_id = len(processed_files['postal'])

        start = len(processed_files['commune'])
        update_commune(current_id, processed_files, postal_dict[key])
        end = len(processed_files['commune'])

        tuple_value = key + (start, end, id_ref)
        processed_files['postal'].append(tuple_value)


def update_commune(id_ref, processed_files, commune_dict):
    for key in commune_dict.keys():
        current_id = len(processed_files['commune'])

        start = len(processed_files['voie'])
        update_voie(current_id, processed_files, commune_dict[key])
        end = len(processed_files['voie'])

        localisation_list = [value for k, value in commune_dict[key].items()]
        lon, lat = tuple_list_mean(localisation_list, range(2))

        tuple_value = key + (lon, lat, start, end, id_ref)
        processed_files['commune'].append(tuple_value)


def update_voie(id_ref, processed_files, voie_dict):
    for key in voie_dict.keys():
        current_id = len(processed_files['voie'])

        start = len(processed_files['localisation'])
        update_localisation(current_id, processed_files, voie_dict[key])
        lon, lat = tuple_list_mean(voie_dict[key], range(2, 4))

        end = len(processed_files['localisation'])

        tuple_value = key + (lon, lat, start, end, id_ref)
        processed_files['voie'].append(tuple_value)

        # Gambiarra - não me orgulho disso
        voie_dict[key] = (lon, lat)


def update_localisation(id_ref, processed_files, localisation_set):
    for localisation in localisation_set:
        tuple_value = localisation + (id_ref, )
        processed_files['localisation'].append(tuple_value)


def tuple_list_mean(tuple_list, indices):
    return (int(np.mean([int(value[index]) for value in tuple_list]))
            for index in indices)
