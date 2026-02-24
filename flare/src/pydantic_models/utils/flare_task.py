from typing import List, Optional

from pydantic import BaseModel, Field


class FlareTask(BaseModel):
    """
    The base yaml that every stage must follow
    """

    cmd: str
    args: List[str]
    output_file: str
    on_completion: Optional[List[str]] = Field(default_factory=list)
    pre_run: Optional[List[str]] = Field(default_factory=list)
    requires: Optional[str] = Field(
        default_factory=str,
    )
