from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from flare.src.pydantic_models.utils import StageModel


class AddStageModel(StageModel):
    required_by: List[str] = Field(default_factory=list)
    requires: str = Field(default_factory=str)

    @root_validator
    def check_at_least_one(cls, values):
        if not values.get("required_by") and not values.get("requires"):
            raise ValueError(
                "At least one of 'required_by' or 'requires' must be provided"
            )
        return values


class UserConfigModel(BaseModel):
    name: str = Field(default="default_name")
    version: str = Field(default="1.0")
    description: str = Field(default="No Description")
    studydir: Path | str = Field(default_factory=Path.cwd)
    outputdir: Path | str = Field(default_factory=Path.cwd)
    add_stage: Optional[Dict[str, AddStageModel]] = Field(default_factory=dict)

    class Config:
        extra = "allow"

    @validator("add_stage", pre=True, always=True)
    def lowercase_keys(cls, v):
        if isinstance(v, dict):
            return {k.lower(): v for k, v in v.items()}
        return v

    @property
    def extra_config_settings(self):
        """Here we capture any additional arguments set by the user
        Specifically this would be things like:
        ```YAML
        batch_system = 'slurm',

        ```
        """
        return {k: v for k, v in self.__dict__.items() if k not in self.__fields__}
