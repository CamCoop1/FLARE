[![CI](https://img.shields.io/github/actions/workflow/status/CamCoop1/FLARE/ci.yaml?style=flat-square&label=CI)](https://github.com/CamCoop1/FLARE/actions/workflows/ci.yaml)
[![Zenodo DOI](https://img.shields.io/badge/Zenodo-10.5281/zenodo.15694628-blue?style=flat-square&logo=zenodo)](https://doi.org/10.5281/zenodo.15694628)
[![CPC DOI](https://img.shields.io/badge/CPC-10.1016/j.cpc.2026.110062-blue?style=flat-square&logo=doi)](https://doi.org/10.1016/j.cpc.2026.110062)
[![Website](https://img.shields.io/badge/Website-FLARE-blue?style=flat-square)](https://camcoop1.github.io/FLARE/)

FLARE is a workflow management tool designed to automate and streamline the use of tools made available in the [Key4HEP](https://github.com/key4hep) turnkey software for future colliders.

## Hot Links 

- [FCCAnalyses Workflows](fccanalyses_workflow.md)
- [Monte Carlo Production Workflows](mc_production/main.md)

## Workflow Settings with `flare.yaml`

Here we discuss how the `flare.yaml` is used to define some key info

- name
- version
- something else im pretty sure?

Also set any [b2luigi](https://b2luigi.belle2.org/) settings also like batch system 

``` YAML

# flare.yaml 
batch_system: lsf
```
