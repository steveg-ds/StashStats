from typing import Any, Optional
from pydantic import AliasChoices, BaseModel, Field, field_validator
from ..utils.model_config import MODEL_CONFIG

class Pattern(BaseModel):
    """
    Pydantic model representing a Ravelry pattern.
    """
    model_config = MODEL_CONFIG

    id: int = Field(alias="id")
    name: str = Field(alias="name")
    permalink: str = Field(alias="permalink")
    designer_name: str = Field(
        ...,
        validation_alias=AliasChoices("designer_name", "designer"),
    )
    free: Optional[bool] = Field(default=None)

    @field_validator('designer_name', mode='before')
    def get_designer_name(cls, v: Any) -> str:
        """
        Resolve designer name from a nested dict or plain string.
        """
        if isinstance(v, dict):
            return v.get('name', '')
        return str(v)
