![CI](https://github.com/amanmdesai/FCC_Software_Framework/actions/workflows/ci.yaml/badge.svg)

# FLARE: FCCee b2Luigi Automated Reconstruction and Event processing

Framework powered by b2luigi to enable streamlined use of MC generators and fccanalysis commandline tool.

# Install
To install the package, follow the basic install process. It is recommended you use a virtual environment. To begin, setup the fcc software from cvmfs

```
$ source /cvmfs/fcc.cern.ch/sw/latest/setup.sh
```

Create a virtual environment

```
$ python3 -m venv .venv
```

To activate the virtual environment use the following command:

```
$ source .venv/bin/activate
```

Lastly, you can install the framework to your virtual environment

```
$ cd FLARE && pip3 install -e .
```

Now your virtual environment will be setup like so:

```
(venv)$
```

# Setting Up Your Analysis

To begin, you can place all of your analysis scripting and tooling inside the `analysis` directory. For the framework to operate as intended, you need to follow these rules:

1. Your analysis stage scripts must be prefixed by which stage it is, as per the `Stages` enum in src/utils/stages.py. What this boils down to is your stage 1 analysis script must be named `stage1_{detailed name}.py`, likewise your final stage analysis script must be named `final_{detailed name}.py`. This is necessary as these prefixes are how the framework knows what stages need to be ran for your analysis.

2. You must not define an `inputDir` or `outputDir` variable in your analysis scripts for any stage. These are reserved for b2luigi to determine during runtime. The only exception is the very first stage or your analysis requires an `inputDir` to define where to look for the MC. The framework checks during runtime if you have accidentally added one of these variables to your scripts and lets you know what you need to change to fix it. Apart from this, you the analyst can define your analysis scripts are you usually would, including adding additional `includePaths` and so forth.

The last thing that requires attention is the `settings.json` located in the root of the FLARE framework. This is where you can globally set any b2luigi settings you require, specifically you must define the batch system you require b2luigi to submit to. You must set the `batch_system` value inside `settings.json` to one of the following, depending on your required batch system:

- lsf
- htcondor
- slurm
- local

Note, if 'local' is set then b2luigi will not submit to the batch system instead just submitting to the head node that you are currently on. This is usually for when your batch system is not available in b2luigi or you wish to do some basic testing.

For more details on the available batch systems see [b2luigi Batch System Specific Settings](https://b2luigi.belle2.org/usage/batch.html?highlight=batch#batch-system-specific-settings). Note some batch systems require/allow for you to pass batch-specific arguments using `settings.json`.

## Running Your Analysis

To run the framework simply go to the command line and run

```
(venv)$ python3 run_analysis.py
```

This will begin the b2luigi workflow and all stages of your analysis will run in sequence. All outputs are located inside the `data` directory.

## Running New/Altered Analysis

You will notice the data directory structure is based off the information provided inside of `analysis/config/details.yaml`. This is helpful as if you make changes to your analysis you can change the `Version` variable inside this yaml file and this will allow b2luigi to run another analysis workflow for you. You will note that once you have ran the workflow once and it was successful you cannot run it again without changing the details in the `details.yaml`.

If you are just running a newer version of an analysis, bump the version number. If instead you have created a parallel analysis which you wish to run, change the name in the `details.yaml` to create a separate branching directory inside the data directory.

# Setting Up MC Production

If MC production is required then a `analysis/mc_production` directory is required. Inside this directory you will find a `details.yaml` file that has a format something like:

``` yaml
"$schema": "src/schemas/mc_production_details.json"

prodtype: whizard

datatype:
    - list
    - of
    - datatypes
```

The details of this yaml file will be explained shortly. The definitions and layout are exact and will always be checked by a JSON checker. It is important that you follow the template.

## Whizard + DelphesPythia6 Production
If you require whizard for you MC production, you will require the following:

### details.yaml

To select the whizard, we must set the `prodtype = whizard`. Under `datatype` you must list all the datatypes you will be generating.
The exact names are of your own choosing and can be as detailed or simple as you like. An example `details.yaml` can be seen below

``` yaml
"$schema": "src/schemas/mc_production_details.json"

prodtype: whizard

datatype:
    - wzp6_ee_mumuH_Hbb_ecm240
    - wzp6_ee_mumuH_HWW_ecm240
```
## Input Files
To run the whizard + DelphesPythia6 workflow the following files must be located in the `analysis/mc_production`:

- < datatype >.sin
- card_<>.tcl
- edm4hep_<>.tcl

Where <> indicates areas where you can input your own naming conventions. The software checks for the key words and suffixes. Note that there must be a `.sin` file for each datatype. Using our example `details.yaml` from above, we would need two `.sin` files:

- wzp6_ee_mumuH_Hbb_ecm240.sin
- wzp6_ee_mumuH_HWW_ecm240.sin

**IMPORTANT:** The `< datatype >.sin` file must have its output file named `proc`. Ensure each `.sin` file has the correct output file name. If not the software will not be able to work correctly.



## Madgraph + DelphesPythia8

### details.yaml

To select the madgraph, we must set the `prodtype = madgraph`. Under `datatype` you must list all the datatypes you will be generating.
The exact names are of your own choosing and can be as detailed or simple as you like. An example `details.yaml` can be seen below

``` yaml
"$schema": "src/schemas/mc_production_details.json"

prodtype: madgraph

datatype:
    - p8_ee_mumuH_Hbb_ecm240
    - p8_ee_mumuH_HWW_ecm240
```

## Input Files
To run the madgraph + DelphesPythia8 workflow the following files must be located in the `analysis/mc_production`:

- < datatype >_runcard.dat
- card_<>.tcl
- edm4hep_<>.tcl
- pythia_card_<>.cmd

Where <> indicates areas where you can input your own naming conventions. The software checks for the key words and suffixes. There must be a `.dat` file for each datatype. Using our example `details.yaml` from above, we would need two `.dat` files:

- p8_ee_mumuH_Hbb_ecm240_runcard.dat
- p8_ee_mumuH_HWW_ecm240_runcard.dat


**IMPORTANT:** The `pythia_card_<>.cmd` file must have the variable `Beams:LHEF = signal.lhe`. If this is
not present, the software will be unable to run the `DelphesPythia8_EDM4HEP` command.


## Running the MC Production

Once you have selected your MC production type and ensured all input files are present adhering to naming conventions and required output file names (see **IMPORTANT** notes ) you are ready to run your MC production.

This can be done is one of two ways. If you wish to *just* produce the MC for now run the following command provided you have followed the instructions in [Install](#install)

```
(venv)$ python3 run_mc_production.py
```

If you instead wish to run the full workflow, that is from the start of MC production all the way to producing plots using `fcc plots` and provided you have followed the instructions in [Setting Up Your Analysis](#setting-up-your-analysis)

```
(venv)$ python3 run_analysis.py
```
