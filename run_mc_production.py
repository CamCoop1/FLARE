import b2luigi as luigi

from src.mc_production.mc_production_types import get_mc_production_types
from src.mc_production.tasks import MCProductionWrapper
from src.utils.logo import print_b2luigi_logo
from src.utils.yaml import get_config


def _check_mc_prod_valid(prodtype: str):
    try:
        _ = get_mc_production_types()[prodtype]
    except KeyError:
        raise KeyError(
            f'MC production type {prodtype} is not valid. Valid prod types are {" ".join(get_mc_production_types().values())}'
        )


if __name__ == "__main__":
    print_b2luigi_logo()
    config = get_config("details.yaml", dir="analysis/mc_production")
    _check_mc_prod_valid(config["prodtype"])
    luigi.process(
        MCProductionWrapper(prodtype=config["prodtype"]), workers=4, batch=True
    )
