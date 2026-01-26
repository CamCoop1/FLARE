from collections.abc import Mapping
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel


class ForbidExtraBaseModel(BaseModel):
    """Define a BaseModel that forbids extra to reject
    unexpected fields. Pydantic v1 allowed extra fields by default and so
    we needed this class to set the allow_extra=False. However, in Pydantic v2
    extra fields are disallowed by default and so this class is not truly necessary
    but alas.
    """


class StageModel(ForbidExtraBaseModel):
    """
    The base yaml that every stage must follow
    """

    cmd: str
    args: List[str]
    output_file: str
    on_completion: Optional[List[str]] = Field(default_factory=list)
    pre_run: Optional[List[str]] = Field(default_factory=list)


class ProductionTypeBaseModel(
    RootModel[Dict[str, StageModel]],
    Mapping[str, StageModel],
):
    """
    Root model mapping production-type name -> StageModel
    """

    def __getitem__(self, key: str) -> StageModel:
        return self.root[key]

    def __len__(self) -> int:
        return len(self.root)
