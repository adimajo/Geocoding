# -*- coding: utf-8 -*-
"""Update the raw data used as the main source of information.

"""
import gzip
import hashlib
import os
import shutil
import sys

import requests
from loguru import logger
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from geocoder.geocoding.datapaths import here, database
from geocoder.geocoding import DEBUG

SSL_VERIFICATION = os.environ.get("SSL_VERIFICATION", False)

if not SSL_VERIFICATION:
    disable_warnings(InsecureRequestWarning)

raw_data_folder_path = os.path.join(here, 'raw')
ban_url = 'https://adresse.data.gouv.fr/data/ban/adresses-odbl/latest/csv/{}'
ban_dpt_gz_file_name = ['adresses-{}.csv.gz', 'lieux-dits-{}-beta.csv.gz']
ban_dpt_file_name = [filegz[:-3] for filegz in ban_dpt_gz_file_name]
content_folder_path = os.path.join(here, 'content')
server_content_file_name = os.path.join(content_folder_path, 'server_content_v2.txt')
local_content_file_name = os.path.join(content_folder_path, 'local_content_v2.txt')
if DEBUG:
    dpt_list = ["01"]
else:  # pragma: no cover
    dpt_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09",
                "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
                "2A", "2B", "21", "22", "23", "24", "25", "26", "27", "28", "29",
                "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
                "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
                "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
                "60", "61", "62", "63", "64", "65", "66", "67", "68", "69",
                "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
                "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
                "90", "91", "92", "93", "94", "95",
                "971", "972", "973", "974", "975", "976", "977", "978", "984", "986", "987", "988", "989"]


def completion_bar(msg: str, fraction: float):
    """
    Writes a completion bar to std out

    Args:
        msg (str): message to write
        fraction (float): fraction of job done
    """
    percent = int(100 * fraction)
    size = int(50 * fraction)
    sys.stdout.write("\r%-16s: %3d%%[%s%s]\n" %
                     (msg, percent, '=' * size, ' ' * (50 - size)))
    sys.stdout.flush()

    # New line if bar is complete
    if fraction == 1.:
        print('')


def md5(fname):
    """
    Calculates md5 hash of file

    Args:
        fname: file path
    """
    md5_hash = hashlib.md5()  # nosec
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def update_ban_file(url, file_name):
    """
    Check which files are present

    Args:
        url (str): URL of BAN database
        file_name (os.Path): name of the file to write
    """
    try:
        msg = 'Unable to join BAN address website ({}).'.format(url)
        r = requests.get(url, verify=SSL_VERIFICATION)
        msg += ' Status error code: {}'.format(r.status_code)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError(msg)
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.HTTPError):
        raise ConnectionError(msg)  # pragma: no cover

    with open(file_name, 'w') as file:
        file.write(r.text)


def update_local_content_file():
    update_ban_file(ban_url.format(""), local_content_file_name)


def update_server_content_file():
    update_ban_file(ban_url.format(""), server_content_file_name)


def need_to_download():
    """
    Defines whether new data needs to be downloaded

    :rtype: bool
    """
    if not os.path.exists(local_content_file_name):
        return True
    else:
        update_server_content_file()

        if md5(server_content_file_name) == md5(local_content_file_name) and os.path.exists(database):
            logger.info('BAN database is already up to date. No need to download it again.')
            os.remove(server_content_file_name)
            return False

        return True


def download_ban_dpt_file(ban_dpt_file_name):
    """
    Downloads a single file from BAN

    Args:
        ban_dpt_file_name (str): name of file to download

    :rtype: bool
    """
    with open(os.path.join(raw_data_folder_path, ban_dpt_file_name), 'wb') as ban_dpt_file:
        response = requests.get(ban_url.format(ban_dpt_file_name), stream=True,
                                verify=SSL_VERIFICATION)

        if not response.ok:  # pragma: no cover
            logger.info('Download {} unsuccessful: bad response'.format(ban_dpt_file_name))
            return False

        done, total_size = 0, int(response.headers.get('content-length'))
        for block in response.iter_content(4096):
            ban_dpt_file.write(block)
            done += len(block)

    if done != total_size:  # pragma: no cover
        logger.error('Download {} unsuccessful: incomplete'.format(ban_dpt_file_name))
        return False

    return True


def get_ban_file():
    """
    Downloads everything if necessary

    Returns: whether a download has been preformed
    :rtype: bool
    """
    if not os.path.exists(content_folder_path):
        os.mkdir(content_folder_path)

    if not need_to_download():
        return False

    logger.info('A new version of BAN base is available.')

    update_local_content_file()

    if os.path.exists(raw_data_folder_path):
        shutil.rmtree(raw_data_folder_path)

    os.mkdir(raw_data_folder_path)

    count = 0
    for dpt in dpt_list:
        for ban_dpt_gz_file_name_type in ban_dpt_gz_file_name:
            downloading_ban_dpt_gz_file_name = ban_dpt_gz_file_name_type.format(dpt)
            if not download_ban_dpt_file(downloading_ban_dpt_gz_file_name):
                logger.error('Impossible to download {}'.format(downloading_ban_dpt_gz_file_name))
        count += 1
        completion_bar('Downloading BAN files', count / len(dpt_list))

    return True


def decompress():
    """
    Decompress every downloaded archive

    Returns: whether decompression was successful
    :rtype: bool
    """
    count = 0
    for dpt in dpt_list:
        # Certifies the existence of the subdirectory.
        for ban_dpt_gz_file_name_type in ban_dpt_gz_file_name:
            dpt_gz_file_path = os.path.join(raw_data_folder_path, ban_dpt_gz_file_name_type.format(dpt))
            if not os.path.isfile(dpt_gz_file_path):  # pragma: no cover
                logger.error('Decompression unsuccessful: nonexistent file {}'.format(dpt_gz_file_path))
                count += 1

            else:  # Decompress each file within gzip
                with gzip.open(dpt_gz_file_path, 'rb') as f_in:
                    dpt_file_path = os.path.join(raw_data_folder_path, ban_dpt_gz_file_name_type.format(dpt)[:-3])
                    logger.info('Extracting file {}'.format(ban_dpt_gz_file_name_type.format(dpt)[:-3]))
                    with open(dpt_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                remove_file(dpt_gz_file_path)

    if count:  # pragma: no cover
        return False
    return True


def remove_file(file_path):
    """
    Delete file

    Args:
        file_path (os.Path): path to file to be deleted
    """
    logger.info('Deleting file {}'.format(file_path))
    try:
        os.remove(file_path)
    except Exception:  # nosec
        pass


def remove_downloaded_raw_ban_files():
    """
    Removes all raw files (compressed and uncompressed)

    Returns: whether removing was successful
    :rtype: bool
    """
    for dpt in dpt_list:
        for ban_dpt_gz_file_name_type in ban_dpt_gz_file_name:
            remove_file(os.path.join(raw_data_folder_path, ban_dpt_gz_file_name_type.format(dpt)))
        for ban_dpt_gz_file_name_type in ban_dpt_file_name:
            remove_file(os.path.join(raw_data_folder_path, ban_dpt_gz_file_name_type.format(dpt)))
    shutil.rmtree(raw_data_folder_path)
    return True
