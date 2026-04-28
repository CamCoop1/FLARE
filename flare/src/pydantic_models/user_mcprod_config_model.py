from typing import Dict, List, Literal, Optional

from pydantic import Field, model_validator

from flare.src.pydantic_models.production_types_model import MCProductionModel
from flare.src.pydantic_models.utils import ForbidExtraBaseModel

# We define here the valid prodtypes, keeping the valid types central to
# the MCProductionModel pydantic model. There is no point importing the production_types.yaml
# As this is dependent on the MCProductionModel anyway. And so we keep it centralised there
VALID_PRODTYPES = ("default", *tuple(MCProductionModel.__fields__.keys()))


class DatatypeBundle(ForbidExtraBaseModel):
    datatype: str
    card: str
    prodtype: str
    edm4hep: str


class DataTypeEntryModel(ForbidExtraBaseModel):
    card: Optional[str] = None
    prodtype: Optional[str] = None

    @model_validator(mode="after")
    def check_prodtype(self):
        if self.prodtype:
            assert (
                self.prodtype in VALID_PRODTYPES
            ), f"Invalid prodtype '{self.prodtype}' in datatype entry. Valid types are {', '.join(VALID_PRODTYPES)}"
        return self


class UserMCProdConfigModel(ForbidExtraBaseModel):
    """
    This is the model that defines the User MC Production yaml file

    Users wishing to use the mc production capabilities of flare must adhere to this
    structure
    """

    datatype: Dict[str, Optional[DataTypeEntryModel]] = {}
    global_prodtype: Literal[*VALID_PRODTYPES] = Field(default="default")
    global_env_script_path: str = Field(default="")
    card: List[str] = Field(default=["default"])
    edm4hep: List[str] = Field(default=["default"])
    k4run_sandbox: str = Field(default="")

    # @model_validator(mode="after")
    # def check_detector_cards(self):
    #     print(self.datatype)
    #     if self.card:
    #         assert any(dt.card for dt in self.datatype.values()), (
    #             "You cannot set the global card variable in your MC Production config yaml as well as the datatype specific card."
    #         )

    def get_datatype_bundle(self, datatype: str):
        """
        For a given datatype, we will fill in our DatatypeBundle model with every unique combination
        of variables as defined by the user inside their mcproduction user YAML
        """
        fields = {f: None for f in DatatypeBundle.__fields__.keys()}
        # Fill in the datatype field
        fields["datatype"] = datatype

        # Set the prodtype for this bundle
        if self.global_prodtype != "default":
            fields["prodtype"] = self.global_prodtype
        else:
            fields["prodtype"] = self.datatype[datatype].prodtype

        # TODO fix this edm4hep step
        fields["edm4hep"] = self.edm4hep[0]

        # Set the card and yield the fields
        if "default" not in self.card:
            for card in self.card:
                fields["card"] = card
                yield DatatypeBundle(**fields)
        else:
            fields["card"] = self.datatype[datatype].card
            yield DatatypeBundle(**fields)

    @property
    def datatype_bundles(self):
        """
        This property will yield each unique bundle of datatype that we must run. This includes
        all unique combinations of

        - datatype
        - detector card
        - production type
        - edm4hep card
        """
        for dt in self.datatype:
            yield from self.get_datatype_bundle(dt)
