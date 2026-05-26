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
