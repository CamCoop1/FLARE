from flare.src.pydantic_models.production_types_model import (
    FCCProductionModel,
    MCProductionModel,
)
from flare.src.pydantic_models.user_config_model import (  # noqa
    AddFlareTask,
    UserConfigModel,
)
from flare.src.pydantic_models.user_mcprod_config_model import UserMCProdConfigModel
from flare.src.pydantic_models.utils import FlareTask, ProductionTypeBaseModel  # noqa

models = dict()

for model in [
    FCCProductionModel,
    MCProductionModel,
    UserMCProdConfigModel,
    UserConfigModel,
]:
    models[model.__name__] = model
