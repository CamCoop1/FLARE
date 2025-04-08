from typing import List, Literal

from pydantic import Field, root_validator

from flare.src.pydantic_models.utils import ForbidExtraBaseModel


class UserMCProdConfigModel(ForbidExtraBaseModel):
    """
    This is the model that defines the User MC Production yaml file

    Users wishing to use the mc production capabilities of flare must adhere to this
    structure
    """

    datatype: List[str | dict]
    global_prodtype: Literal["madgraph", "whizard", "pythia8"] = Field(
        default="default"
    )
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
                prodtypes = ("madgraph", "whizard", "pythia8")
                if inner_prodtype not in prodtypes:
                    raise ValueError(
                        f"Invalid prodtype '{inner_prodtype}' in datatype entry. Valid types are {', '.join(prodtypes)}"
                    )
        return values
