---
id: getting-started
title: Getting Started
sidebar_label: Getting Started
next_page: cli
previous_page: home
---
FLARE can be accessed from two sources, from the `key4HEP` nightly stack or from PyPI. 

## Access from key4HEP
The [key4HEP](https://key4hep.github.io/key4hep-doc/main/index.html) is an open source turnkey software package that provides access to high quality proven HEP software solutions for all. It includes an huge number of commandline tools for generating Monte Carlo simulation data for any experiment configuration. It also includes its own analysis tooling by way of the [FCCAnalyses](https://hep-fcc.github.io/FCCAnalyses/doc/latest/).

The `key4HEP` is provided via the [CernVM File System](https://cvmfs.readthedocs.io/en/stable/), also known as the `CVMFS`. To gain access to FLARE one must source the nightly version of `key4HEP`:

``` bash
$ source < INSERT PATH TO NIGHTLY STACK>
```

## Install from PyPI
To install fro PyPI, follow this basic install process. It is recommended you use a virtual environment. To begin, a working version of python>3.8 must be installed on your system. If one is not natively avaiable, setup the `key4HEP` software from the `CVMFS`.

```
$ source /cvmfs/fcc.cern.ch/sw/latest/setup.sh
```

Next, create a virtual environment. This can be done in many ways however, the simplest is to use the `venv` package provided by python.

```
$ python3 -m venv .venv
```

To you virtual environment. If `venv` was used, run following command:

```
$ source .venv/bin/activate
```

Lastly, you can install `hep-flare` to your virtual environment. An example is shown below using `pip`.

```
(.venv)$ pip3 install hep-flare
```

## Running Your First FLARE Workflow
Here we will clone the [FLARE Examples](https://github.com/CamCoop1/FLARE-examples) repository to access the many examples available within. 

``` bash
(.venv)$ git clone https://github.com/CamCoop1/FLARE-examples
(.venv)$ cd FCCAnalysis_workflow/higgs_mass_example
```

In this example, the `FCCAnalyses` tool is going to be utilized to orchestrate and run an analysis workflow investigating the Higgs mass at the FCCee. 

**NOTE** that inside the `flare.yaml`, the `batch_system=slurm`. If your machine does not support slurm you can change this to one of the following

- `htcondor`
- `lsf`
- `local`

Where `local` will mean FLARE does not submit to any batch system. Instead it will run the entire workflow on your local working node.

To run this workflow, invoke the [FLARE Commandline Tool](cli.md) as shown below.

``` bash
(.venv)$ flare run analysis
```

### How The FCCAnalyses Workflow Is Staged
This workflow is staged by having three `FCCAnalyses` steering script, each prefixed to indicate the order in which FLARE will run these tasks. That is 

- **stage1_**flavor.py
- **stage2_**histamaker_flavor.py
- **plots_**flavor.py

At a maximum FLARE can orchestrate and run:

1. stage1
2. stage2
3. stage3
4. final
5. plots

The hierachy is always upheld but a user need not use all the avaiable prefixes. For example, one could stage their FLARE workflow with the following files 

``` bash
$ ls
$ stage2_test.py stage3_test.py plots_test.py
```

FLARE will reference its heirachy and schedule the Tasks such that `stage2 -> stage3 -> plots`.
