# -*- coding: utf-8 -*-
"""Processing of raw data.

This module creates an intermediary database in csv format. The goal of this
intermediate step is to easy the next step: the construction of the binary
files using tools from the package numpy.

"""

import os
import shutil
from collections import deque, defaultdict

import numpy as np
from loguru import logger
from tqdm import tqdm

from geocoder.geocoding import ban_processing, LOCAL_DB, s3
from geocoder.geocoding.datapaths import paths, database
from geocoder.geocoding.datatypes import dtypes
from geocoder.geocoding.download import raw_data_folder_path

file_names = ['departement', 'postal', 'commune', 'voie', 'localisation']
processed_files = {}


def _init_processing():
    # Check if the folder with the data to process exists
    if not os.path.exists(raw_data_folder_path):  # pragma: no cover
        logger.info('Data not found - execute: geocoder download')
        return False

    for file in file_names:
        processed_files[file] = deque()
    return True


def process_files():
    """
    Process all downloaded decompressed files

    :return: if processing was successful
    :rtype: bool
    """
    if not _init_processing():
        return False

    ban_files = defaultdict(list)

    # Open each csv file
    for (dirname, dirs, files) in os.walk(raw_data_folder_path):
        for filename in files:
            if filename.endswith('.csv'):
                file_path = os.path.join(dirname, filename)
                if "adresses" in filename:
                    dpt_name = filename.split('-')[-1].split('.')[0]
                else:
                    dpt_name = filename.split('-')[-2].split('.')[0]
                ban_files[dpt_name].append(file_path)

    logger.debug(f"Files: {ban_files}")

    # Check if the folder was not empty
    if not ban_files:  # pragma: no cover
        logger.info('No CSV file - execute: geocoder decompress')
        return False

    departements = list(ban_files.keys())
    departements.sort()

    for departement in tqdm(departements, desc="Process files"):
        for file in ban_files[departement]:
            logger.debug(f"Département : {departement}")
            logger.debug(f"Fichier : {file}")
            ban_processing.update(departement, file, processed_files)

    return True


def create_database():
    if os.path.exists(database):
        try:
            shutil.rmtree(database)
        except PermissionError as e:  # pragma: no cover
            logger.error('Windows sucks, remove database folder manually and proceed.')
            raise e
    os.mkdir(database)

    if not processed_files:  # pragma: no cover
        return False

    add_index_tables()

    for table, processed_file in tqdm(processed_files.items(), desc="Store database"):
        create_dat_file(list(processed_file), paths[table], dtypes[table])

    return True


def add_index_tables():
    index_tables = ['postal', 'commune', 'voie']

    # Index tables creation
    for current_table in tqdm(index_tables, desc="Index tables"):
        sort_method = (lambda j, table=current_table: processed_files[table][j])

        # Sort table and add it to the module level dict processed_files
        processed_files[current_table + '_index'] = \
            sorted(range(len(processed_files[current_table])), key=sort_method)


def create_dat_file(lst, out_filename, dtype):
    """Write a list in a binary file as a numpy array.

    Args:
        lst: The list that will be written in the file.
        out_filename: The name of the binary file. It must be in the same
            directory.
        dtype: The type of the numpy array.
    """
    dat_file = np.memmap(out_filename, mode='w+', dtype=dtype, shape=(len(lst), ))
    dat_file[:] = lst[:]
    dat_file.flush()
    if not LOCAL_DB:
        s3.upload_file(out_filename, "geocoder", f"database/{os.path.basename(out_filename)}")
