#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions relating to directories.
"""

from pathlib import Path

from src.definitions import BASE_DIRECTORY


def find_file(*path, string=False):
    path = Path(BASE_DIRECTORY, *path)
    return str(path) if string else path
