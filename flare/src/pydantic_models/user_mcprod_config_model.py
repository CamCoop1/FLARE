from typing import List, Literal

from pydantic import Field

from flare.src.pydantic_models.utils import ForbidExtraBaseModel


class UserMCProdConfigModel(ForbidExtraBaseModel):
    """
    This is the model that defines the User MC Production yaml file

    Users wishing to use the mc production capabilities of flare must adhere to this
    structure
    """

    datatype: List[str]
    prodtype: Literal["madgraph", "whizard"]
    card: List[str] = Field(default=["default"])
    edm4hep: List[str] = Field(default=["default"])
