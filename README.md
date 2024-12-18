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
