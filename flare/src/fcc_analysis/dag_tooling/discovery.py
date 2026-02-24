"""
This module serves to discovery the active FCCAnalysis stages that we must convert
into FlareTask objects.
"""

from pathlib import Path

import b2luigi as luigi


def discover_task_scripts() -> list[str]:
    """
    This function alone will hold the logic for finding the FCC Analysis Task scripts
    that are required by the analyst. Because FLARE is designed to allow the user to just
    define create their python scripts in the CWD and we identify what FCC Analysis stages
    must be ran from that. This all must happen at run time.
    """
    studydir = luigi.get_setting("study_dir", Path.cwd())
    # Grab the valid internal tasks, the names of which define the task
    # I.e stage1.py would be picked up as stage1
    valid_internal_task_names = luigi.get_setting("internal_fcc_analysis_tasks").keys()
    # The identified Tasks consistent with those defined in valid_internal_task_names
    identified_tasks = [
        p.stem.split("_")[0]
        for p in studydir.glob("*.py")
        # This if-statement ensures we only keep the discovered python files
        # that begin with a VALID FCC Analysis Task identifier
        if any(p.stem.startswith(x) for x in valid_internal_task_names)
    ]
    # Check that there are no double-ups of Task files
    assert len(identified_tasks) == len(
        set(identified_tasks)
    ), "More than more python script exists with the same FCC Analysis Task idenfier prefix. Please fix this and rerun"
    return identified_tasks  # Returned as an ordered list


def get_python_script_for_task(task: str) -> Path:
    studydir = luigi.get_setting("studydir")
    # This is guaranteed since this function is only ever called after all validation is done
    python_script = [p for p in studydir.glob("*py")][0]
    return python_script
