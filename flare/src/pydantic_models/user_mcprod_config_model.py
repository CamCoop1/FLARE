from typing import List, Literal

from pydantic import Field, root_validator

from flare.cli.logging import logger
from flare.src.pydantic_models.production_types_model import MCProductionModel
from flare.src.pydantic_models.utils import ForbidExtraBaseModel

# We define here the valid prodtypes, keeping the valid types central to
# the MCProductionModel pydantic model. There is no point importing the production_types.yaml
# As this is dependent on the MCProductionModel anyway. And so we keep it centralised there
VALID_PRODTYPES = tuple(MCProductionModel.__fields__.keys())


class UserMCProdConfigModel(ForbidExtraBaseModel):
    """
    This is the model that defines the User MC Production yaml file

    Users wishing to use the mc production capabilities of flare must adhere to this
    structure
    """

    datatype: List[str | dict]
    global_prodtype: Literal[VALID_PRODTYPES] = Field(default="default")
    global_env_script_path: str = Field(default="")
    card: List[str] = Field(default=["default"])
    edm4hep: List[str] = Field(default=["default"])

    @root_validator
    def check_prodtype_and_datatype(cls, values):
        prodtype = values.get("global_prodtype")
        datatype = values.get("datatype")

        if prodtype != "default":
            assert isinstance(
                datatype, list
            ), "When setting a global_prodtype, the datatype must be a list"
            assert all(
                isinstance(x, str) for x in datatype
            ), "When setting a global_prodtype, each type in the datatype list must be a string"
            return values

        if not isinstance(datatype, list):
            raise ValueError("datatype must be a list")
        for item in datatype:
            if not isinstance(item, dict):
                raise ValueError(
                    "When prodtype is 'default', each datatype must be a dictionary e.g {'my_data' : {'prodtype': 'whizard'}}"
                )
            if len(item) != 1:
                raise ValueError(
                    "Each datatype dictionary must have exactly one key e.g {'my_data' : {'prodtype': 'whizard'}}"
                )
            for val in item.values():
                if not isinstance(val, dict):
                    raise ValueError(
                        "The value of each datatype entry must be a dictionary e.g {'my_data' : {'prodtype': 'whizard'}}"
                    )
                inner_prodtype = val.get("prodtype", None)
                if not inner_prodtype:
                    raise ValueError(
                        "There is no prodtype in the datatype dictionary e.g {'my_data' : {'prodtype': 'whizard'}} "
                    )

                if inner_prodtype not in VALID_PRODTYPES:
                    raise ValueError(
                        f"Invalid prodtype '{inner_prodtype}' in datatype entry. Valid types are {', '.join(VALID_PRODTYPES)}"
                    )

            global_env_script_path = values.get("global_env_script_path")

            if global_env_script_path:
                logger.info(
                    "\033[31mIMPORTANT\033[0m: you have set a global environment script path to be setup on the submitted batch job.\n"
                    "If you are using a virtual environment (you should be!!!) you must also activate your virtual environment like so:\n\n"
                    "    source fcc/tool/distro/setup.sh\n"
                    "    source path/to/my/.venv/bin/activate"
                )
        return values
