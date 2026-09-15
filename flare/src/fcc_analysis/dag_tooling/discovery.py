"""
This module serves to discovery the active FCCAnalysis stages that we must convert
into FlareTask objects.
"""

from pathlib import Path

import b2luigi as luigi


def discover_task_scripts() -> list[str]:
    studydir = luigi.get_setting("studydir", Path.cwd())

    valid_internal_task_names = list(
        luigi.get_setting("internal_fcc_analysis_tasks").keys()
    )

    identified_tasks = [
        p.stem.split("_")[0]
        for p in studydir.glob("*.py")
        if any(p.stem.startswith(x) for x in valid_internal_task_names)
    ]

    assert len(identified_tasks) == len(
        set(identified_tasks)
    ), "More than one python script exists with the same FCC Analysis Task identifier prefix. Please fix this and rerun"

    # Order deterministically according to the canonical internal task order,
    # not filesystem/glob iteration order (which varies across OS/filesystems)
    identified_tasks.sort(key=valid_internal_task_names.index)

    return identified_tasks


def get_python_script_for_task(task: str) -> Path:
    studydir = luigi.get_setting("studydir")
    # This is guaranteed since this function is only ever called after all validation is done
    python_script = [p for p in studydir.glob("*py") if task in p.name]

    assert (
        len(python_script) == 1
    ), f"The python script for {task} could not be found in {studydir}"
    return python_script[0]
