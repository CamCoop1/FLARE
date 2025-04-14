#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions relating to directories.
"""
from pathlib import Path

from b2luigi import get_setting

from flare.src.definitions import BASE_DIRECTORY


def find_file(*path, string=False):
    """
    Using the BASE_DIRECTORY, this function will find any file
    inside the framework
    """
    path = Path(BASE_DIRECTORY, *path)
    return str(path) if string else path


def find_external_file(*path, string=False):
    cwd = get_setting("working_dir")

    path = Path(cwd, *path)
    return str(path) if string else path
