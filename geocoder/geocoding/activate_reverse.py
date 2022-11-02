"""
create kdtree for reverse search

.. autosummary::
    create_kdtree
"""
import gc

import numpy as np
from kdquery import Tree
from loguru import logger

from geocoder.geocoding.datapaths import paths
from geocoder.geocoding.datatypes import dtypes
from geocoder.geocoding.download import completion_bar
from geocoder.geocoding.index import create_dat_file
from geocoder.geocoding.utils import pre_order, degree_to_int


def node_to_tuple(node):
    left = node.left if node.left is not None else -1
    right = node.right if node.right is not None else -1

    return node.point + tuple(node.region[0]) + tuple(node.region[1]) + \
        (node.axis, left, right, node.data)


def create_kdtree():
    """
    Creates and stores a kd-tree as a dat file on disk for reverse search of addresses given geolocation

    :rtype: bool
    """
    table = np.memmap(paths['localisation'], dtype=dtypes['localisation'])
    indices = np.argsort(table, order='longitude').astype('int32')

    # Limits of all the French region
    limits = [[degree_to_int(-62), degree_to_int(55)],
              [degree_to_int(-22), degree_to_int(52)]]

    tree = Tree(2, len(table), limits)

    # Load tree with all the addresses on France
    for count, i in enumerate(pre_order(len(table))):
        index = indices[i]
        tree.insert((table[index]['longitude'], table[index]['latitude']),
                    data=index)

        if count % 300000 == 0 or count == len(table) - 1:
            completion_bar('Loading kd-tree', ((count + 1) / len(table)))

    tuple_list = [node_to_tuple(node) for node in tree]

    del tree
    gc.collect()

    logger.info('Saving kdtree...')
    create_dat_file(tuple_list, paths['kdtree'], dtypes['kdtree'])
    logger.info('Done')

    return True
