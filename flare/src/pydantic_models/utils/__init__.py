from pydantic import BaseModel, ConfigDict

from .flare_task import FlareTask  # noqa
from .production_type import ProductionTypeBaseModel  # noqa


class ForbidExtraBaseModel(BaseModel):
    """Define a BaseModel that forbids extra to reject
    unexpected fields"""

    model_config = ConfigDict(extra="forbid")
