.. _cli:

FLARE Commandline Interface
============================

The FLARE Commandline Interface (CLI) is the entry point for all things FLARE. Here we will discuss the various tools within that a user can utilize for their workflow requirements.

FLARE Run
---------

.. code-block:: bash

   $ flare run -- help
   < INSERT THE OUTPUT>
   mcproduction, analysis

The ``run`` method is the entry point in which a user can run their workflow. Currently, there are 2 workflows implemented into FLARE, the ``mcproduction`` and ``analysis``. Irrespective of which one you choose, they have a set of common arguments.

.. code-block:: bash

   options:
     -h, --help            show this help message and exit
     --name NAME           Name of the study
     --version VERSION     Version of the study
     --description DESCRIPTION
                           Description of the study
     --study-dir STUDY_DIR
                           Study directory path where the files for production are located
     --output-dir OUTPUT_DIR
                           The location where the output file will be produced, by default will be the current working directory
     --config-yaml CONFIG_YAML
                           Path to a YAML config file

\-\-name and \-\-version
~~~~~~~~~~~~~~~~~~~~~~~~~

Important to note is that the ``--name`` and ``--version`` options will affect the output directory structure. For example if the following command is ran:

.. code-block:: bash

   flare run analysis --name docs --version 1.0

The output data directory that FLARE creates will have the following structure:

.. code-block:: bash

   data/docs/1.0/...

This design means if a workflow needs to be rerun with slight changes one can just change the name OR version number depending on what suits the user's needs.

\-\-description
~~~~~~~~~~~~~~~

The ``--description`` option allows the user to provide a description of their workflow, what it is achieving or what assumptions one should know if they are to revisit this workflow in the future. The text provided is bundled into a ``README.md`` file located inside the output directory structure, e.g.:

.. code-block:: bash

   ls data/docs/1.0/README.md

\-\-study-dir
~~~~~~~~~~~~~

It is common practice to store your workflow input files in your current working directory. However, this option allows a user to tell FLARE if a different directory contains the input files for the workflow.

.. code-block:: bash

   flare run mcproduction --study-dir ../different_input_files

\-\-output-dir
~~~~~~~~~~~~~~

By default all the output directory structure of FLARE is created in the current working directory. If a user wishes to have the output directory structure located elsewhere, they can provide a path via the ``--output-dir`` option.

.. code-block:: bash

   flare run analysis --output-dir ../../central_FLARE_outputs

FLARE run analysis: \-\-mcprod
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``flare run analysis`` command has one additional argument, namely ``--mcprod``.

Workflow Settings with ``flare.yaml``
--------------------------------------

The ``flare.yaml`` is the configuration file located in your current working directory. This is where FLARE will look for additional configuration settings required for the workflow.

It is also the location in which a user can interact with the `b2luigi <https://b2luigi.belle2.org/>`_ backend settings manager.

Customizable FLARE Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This yaml file allows a user to set the ``--name``, ``--version`` and ``--description`` from the CLI tool. This can simplify the running of a workflow by having these settings defined in this central yaml file rather than adding it to the CLI command each time a workflow is ran.

.. code-block:: yaml

   # flare.yaml
   name: docs
   version: 1.0
   description: This workflow is defined in the documentation

As mentioned, a user can set any `b2luigi <https://b2luigi.belle2.org/>`_ settings here in the ``flare.yaml``. Importantly, this is where a user can set the ``batch_system`` setting, informing FLARE which batch system to submit to. FLARE can submit to the following batch systems:

- Slurm
- LSF
- HTCondor

If your batch system is not available, new ones can easily be added — checkout the `b2luigi docs <https://b2luigi.belle2.org/>`_ for more information.

.. code-block:: yaml

   # flare.yaml
   name: docs
   version: 1.0
   description: This workflow is defined in the documentation

   # b2luigi settings
   batch_system: lsf

FLARE Settings Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   1. CLI Interface
         |
         v
   2. FLARE yaml settings
         |
         v
   3. Default Settings

The FLARE settings manager works on a hierarchy. FLARE prioritizes the settings passed to the CLI. If a setting was not passed there, FLARE will next refer to the ``flare.yaml``. Lastly, if a setting value is not provided, a default is used.

FLARE uses `Pydantic <https://pydantic.dev/docs/validation/latest/get-started/>`_ to validate user input data. The exact Pydantic model along with the defaults are shown below.

.. code-block:: python

   from pathlib import Path

   class UserConfigModel(BaseModel):
       name: str = Field(default="default_name")
       version: str = Field(default="1.0")
       description: str = Field(default="No Description")
       studydir: Path | str = Field(default_factory=Path.cwd)
       outputdir: Path | str = Field(default_factory=Path.cwd)

FLARE lint
----------

.. code-block:: bash

   flare lint fccanalysis

The FLARE linting tool is an addition to version 0.3.0 which will crawl through workflow input files and ensure they are formatted correctly. To use the tool, a user must be in the working directory in which their input workflow files are located.

The FLARE linter is designed to enforce the following FLARE Principles:

- FLARE has full control of the input and output directories of workflow data.
- For each Task required by a user, there must exist a unique script for that step.
- Every Task in FLARE can have at most one required Task. I.e. each Task can have a single input data directory to draw from.

These principles are especially important when utilizing the `Add Custom Tasks <features/add_stage.html>`_ feature of FLARE.
