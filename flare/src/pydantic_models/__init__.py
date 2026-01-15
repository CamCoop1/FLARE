from flare.src.pydantic_models.production_types_model import (
    FCCProductionModel,
    MCProductionModel,
)
from flare.src.pydantic_models.user_config_model import UserConfigModel
from flare.src.pydantic_models.user_mcprod_config_model import UserMCProdConfigModel

models = dict()

for model in [
    FCCProductionModel,
    MCProductionModel,
    UserMCProdConfigModel,
    UserConfigModel,
]:
    models[model.__name__] = model
