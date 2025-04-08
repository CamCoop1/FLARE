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
    The pydantic model for MC Production
    """

    whizard: ProductionTypeBaseModel
    madgraph: ProductionTypeBaseModel
    pythia8: ProductionTypeBaseModel
