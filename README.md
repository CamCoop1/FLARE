# FCC_Software_Framework

Framework powered by b2luigi to enable streamlined use of the fccanalysis commandline tool.

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
$ cd FCC_Software_Framework && pip3 install -e .
```

Now your virtual environment will be setup like so:

```
(venv)$
```

# Setting up your analysis

To begin, you can place all of your analysis scripting and tooling inside the `analysis` directory. For the framework to operate as indended, you need to follow these rules:

1. Your analysis stage scripts must be prefixed by which stage it is, as per the `Stages` enum in src/utils/stages.py. What this boils down to is your stage 1 analysis script must be named `stage1_{detailed name}.py`, likewise your final stage analysis script must be named `final_{detailed name}.py`. This is necessary as these prefixes are how the framework knows what stages need to be ran for your analysis.

2. You must not define an `inputDir` or `outputDir` variable in your analysis scripts for any stage. These are reserved for b2luigi to determine during runtime. The only exception is the very first stage or your analysis requires an `inputDir` to define where to look for the MC. The framework checks during runtime if you have accidently added one of these variables to your scripts and lets you know what you need to change to fix it. Apart from this, you the analyst can define your analysis scripts are you usually would, including adding additional `includePaths` and so forth.

# Running your analysis

To run the framework simply go to the command line and run

```
(venv)$ python3 run_analysis.py
```

This will begin the b2luigi workflow and all stages of your analysis will run in sequence. All outputs are located inside the `data` directory.

# Running new/altered analysis

You will notice the data directory structure is based off the information provided inside of `analysis/config/details.yaml`. This is helpful as if you make changes to your analysis you can change the `Version` variable inside this yaml file and this will allow b2luigi to run another analysis workflow for you. You will note that once you have ran the workflow once and it was successful you cannot run it again without changing the details in the `details.yaml`.

If you are just running a newer version of an analysis, bump the version number. If instead you have created a parallel analysis which you wish to run, change the name in the `details.yaml` to create a seperate branching directory inside the data directory.
