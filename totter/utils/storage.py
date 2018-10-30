""" Module for generating conventional storage paths

Credit: cbarrick's storage module in the Apollo project:
https://github.com/cbarrick/apollo/blob/master/apollo/storage.py

"""

import logging
import os
from pathlib import Path


logger = logging.getLogger(__name__)


def get_root():
    """Set the storage root for persistent data.
    This method reads from the ``TOTTER_STORAGE`` environment variable,
    defaulting to ``totter/results``.

    Returns:
        root (Path): The location of the storage root.

    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    default_storage_dir = os.path.join(parent_dir, 'results')

    root = os.environ.get('TOTTER_STORAGE', default_storage_dir)
    root = Path(root)

    return root


def set_root(root):
    """Set the storage root for persistent data in Apollo.
    This method works by setting the ``TOTTER_STORAGE`` environment variable.

    Arguments:
        root (str or Path): The new location of the storage root.

    Returns:
        old_root (Path): The previous storage root.
    """
    old_root = get_root()
    root = Path(root).resolve()
    os.environ['TOTTER_STORAGE'] = str(root)
    return old_root


def get(component):
    """Access a directory under the storage root.

    Arguments:
        component (str or Path): A path relative to the storage root.
    Returns:
        path (Path):
            An absolute path to a directory under the storage root.
            The directory is automatically created if it does not exist.
    """
    root = get_root()
    path = Path(root) / Path(component)
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path