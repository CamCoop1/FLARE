

from collections.abc import Mapping


from typing import Dict, List, Optional, Iterator

from pydantic import ConfigDict, BaseModel, Field, RootModel


class ForbidExtraBaseModel(BaseModel):
    """Define a BaseModel that forbids extra to reject
    unexpected fields"""
    model_config = ConfigDict(extra="forbid")


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

    def __iter__(self) -> Iterator[str]:
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
