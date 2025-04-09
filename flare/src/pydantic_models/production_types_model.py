from flare.src.pydantic_models.utils import (
    ForbidExtraBaseModel,
    ProductionTypeBaseModel,
)


class FCCProductionModel(ForbidExtraBaseModel):
    """
    The pydantic model for FCC analysis
    """

    fccanalysis: ProductionTypeBaseModel


class MCProductionModel(ForbidExtraBaseModel):
    """
    The pydantic model for MC Production. This model is
    the central place where all MC production types are listed
    """

    whizard: ProductionTypeBaseModel
    madgraph: ProductionTypeBaseModel
    pythia8: ProductionTypeBaseModel
