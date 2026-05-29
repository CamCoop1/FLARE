.. _mcproduction:

MC Production Workflows
~~~~~~~~~~~~~~~~~~~~~~~
FLARE leverages the various Monte Carlo production tools inside key4HEP to build custom user workflows in order to generate any MC automonously. As with any FLARE workflow, staging your workflow is simple.
Just include your required input files inside a `mc_production` subdirectory, include a `flare_mc.yaml` file and run the following command.

.. code-block:: bash

    $ ls mc_production
    flare_mc.yaml <input file 1> <input file 2> ...
    $ flare run mcproduction


.. toctree::
    :maxdepth: 2

    ./fastsim
    ./fullsim
