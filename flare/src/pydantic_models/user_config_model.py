from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flare.src.pydantic_models.utils import StageModel


class AddStageModel(StageModel):
    required_by: List[str] = Field(default_factory=list)
    requires: str = Field(default_factory=str)

    @model_validator(mode="before")
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
    model_config = ConfigDict(extra="allow")

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @field_validator("add_stage", mode="after")
    @classmethod
    def lowercase_keys(cls, v):
        if isinstance(v, dict):
            return {k.lower(): v for k, v in v.items()}
        return v

    @property
    def extra_config_settings(self) -> dict:
        """Capture any additional user-defined config values."""
        return self.model_extra or {}
