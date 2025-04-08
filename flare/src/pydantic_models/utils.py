from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ForbidExtraBaseModel(BaseModel):
    """Define a BaseModel that forbids extra to reject
    unexpected fields"""

    class Config:
        extra = "forbid"


class StageModel(ForbidExtraBaseModel):
    """
    The base yaml that every stage must follow
    """

    cmd: str
    args: List[str]
    output_file: str
    on_completion: Optional[List[str]] = Field(default_factory=list)
    pre_run: Optional[List[str]] = Field(default_factory=list)


class ProductionTypeBaseModel(ForbidExtraBaseModel):
    """
    The ProductionTypeBaseModel that is used to define any
    production type

    We use this to define the fact a ProductionType should is expected
    to be a dictionary with the key being the production type and the
    value being in the format from the Stage model
    """

    # Allows arbitrary keys, each mapping to a Stage
    __root__: Dict[str, StageModel]
