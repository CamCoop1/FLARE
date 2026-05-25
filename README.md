[![CI](https://img.shields.io/github/actions/workflow/status/CamCoop1/FLARE/ci.yaml?style=flat-square&label=CI)](https://github.com/CamCoop1/FLARE/actions/workflows/ci.yaml)
[![Zenodo DOI](https://img.shields.io/badge/Zenodo-10.5281/zenodo.15694628-blue?style=flat-square&logo=zenodo)](https://doi.org/10.5281/zenodo.15694628)
[![CPC DOI](https://img.shields.io/badge/CPC-10.1016/j.cpc.2026.110062-blue?style=flat-square&logo=doi)](https://doi.org/10.1016/j.cpc.2026.110062)
[![Website](https://img.shields.io/badge/Website-FLARE-blue?style=flat-square)](https://camcoop1.github.io/FLARE/)

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

If you are installing from PYPI then use
```
$ pip3 install hep-flare
```
Now your virtual environment will be setup like so:

```
(venv)$
```
## How to Cite: 

@article{CooperHarris:2025lqd, author = "Cooper Harris, Cameron and Desai, Aman", title = "{FLARE: FCCee b2Luigi Automated Reconstruction and Event processing}", eprint = "2506.16094", archivePrefix = "arXiv", primaryClass = "hep-ph", reportNumber = "ADP-25-23/T1285", doi = "10.1016/j.cpc.2026.110062", journal = "Comput. Phys. Commun.", volume = "322", pages = "110062", year = "2026" }
