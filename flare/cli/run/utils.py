import argparse
from pathlib import Path

COMMON_ARGUMENTS = [
    ("--name", {"help": "Name of the study"}),
    ("--version", {"help": "Version of the study"}),
    ("--description", {"help": "Description of the study"}),
    (
        "--study-dir",
        {"help": "Study directory path where the files for production are located"},
    ),
    (
        "--output-dir",
        {
            "help": "The location where the output file will be produced, by default will be the current working directory"
        },
    ),
    ("--config-yaml", {"help": "Path to a YAML config file"}),
    ("--cwd", {"help": argparse.SUPPRESS, "default": Path().cwd()}),
]
