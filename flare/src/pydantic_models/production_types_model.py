from flare.src.pydantic_models.base_stage_model import (
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
