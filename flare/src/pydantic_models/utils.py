from collections.abc import Mapping
from typing import Dict, Iterator, List, Optional

from pydantic import BaseModel, Field, RootModel


class ForbidExtraBaseModel(BaseModel):
    """Define a BaseModel that forbids extra to reject
    unexpected fields"""


class FlareTask(ForbidExtraBaseModel):
    """
    The base yaml that every stage must follow
    """

    cmd: str
    args: List[str]
    output_file: str
    on_completion: Optional[List[str]] = Field(default_factory=list)
    pre_run: Optional[List[str]] = Field(default_factory=list)


class ProductionTypeBaseModel(
    RootModel[Dict[str, FlareTask]],
    Mapping[str, FlareTask],
):
    """
    Root model mapping production-type name -> StageModel
    """

    def __getitem__(self, key: str) -> FlareTask:
        return self.root[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
