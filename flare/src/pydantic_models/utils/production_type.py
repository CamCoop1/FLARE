from collections.abc import Mapping
from typing import Dict

from pydantic import RootModel

from .flare_task import FlareTask


class ProductionTypeBaseModel(
    RootModel[Dict[str, FlareTask]],
    Mapping[str, FlareTask],
):
    """
    Root model mapping production-type name -> StageModel
    """

    def __getitem__(self, key: str) -> FlareTask:
        return self.root[key]

    def __len__(self) -> int:
        return len(self.root)
