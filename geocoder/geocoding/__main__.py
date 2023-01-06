#!/usr/bin/env python3
"""
defines entrypoints
"""
import multiprocessing
import os
import sys
from argparse import ArgumentParser

from geocoder.geocoding import LOCAL_DB
from geocoder.geocoding.activate_reverse import create_kdtree
from geocoder.geocoding.datapaths import paths
from geocoder.geocoding.download import get_ban_file, decompress, remove_downloaded_raw_ban_files
from geocoder.geocoding.index import process_files, create_database
from geocoder.wsgi import runserver


def update():
    if get_ban_file() or (LOCAL_DB and not all([os.path.exists(path) for path in paths])):
        decompress()
        process_files()
        create_database()
        create_kdtree()
    try:
        remove_downloaded_raw_ban_files()
    except Exception:  # nosec
        pass
    return True


commands = {
    'download': [get_ban_file],
    'decompress': [decompress],
    'index': [process_files, create_database],
    'reverse': [create_kdtree],
    'update': [update],
    'clean': [remove_downloaded_raw_ban_files],
    'runserver': [runserver]
}

parser = ArgumentParser(description='Runserver parser')
parser.add_argument('--host', type=str, default='0.0.0.0',  # nosec
                    help='IP to bind')
parser.add_argument('--port', type=str, default='8000',
                    help='port to bind')
parser.add_argument('--worker', type=int, default=(multiprocessing.cpu_count() * 2) + 1,
                    help='number of workers')


def main():
    command = sys.argv[1:]

    if not command or command[0] not in commands:
        print('usage: geocoding '
              '{update, download, decompress, index, clean, reverse}')
        return

    if command[0] == "runserver":
        args, unknown = parser.parse_known_args()
        runserver(vars(args))
    else:
        for function in commands[command[0]]:
            success = function()
            if not success:
                return


if __name__ == "__main__":
    main()
