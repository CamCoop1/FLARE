import b2luigi as luigi

from flare.flare_settings import settings
from flare.src.mc_production.mc_production_types import get_mc_production_types
from flare.src.mc_production.tasks import MCProductionWrapper
from flare.src.utils.logo import print_b2luigi_logo


def _check_mc_prod_valid(prodtype: str):
    try:
        _ = get_mc_production_types()[prodtype]
    except KeyError:
        raise KeyError(
            f'MC production type {prodtype} is not valid. Valid prod types are {" ".join(get_mc_production_types().values())}'
        )


def main(executable=list):
    print_b2luigi_logo()
    config = settings.get_setting("dataprod_config")
    print(config)
    _check_mc_prod_valid(config["prodtype"])
    luigi.set_setting("filename", "")
    luigi.set_setting("executable", executable)
    luigi.process(
        MCProductionWrapper(prodtype=config["prodtype"]),
        workers=4,
        batch=True,
        ignore_additional_command_line_args=True,
    )


if __name__ == "__main__":
    main()
