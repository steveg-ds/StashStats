from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Dict, Any
import dash_bootstrap_components as dbc

from ..utils import MODEL_CONFIG


@dataclass
class BaseComponent:
    __pydantic_config__ = MODEL_CONFIG

    container_id: str = Field(kw_only=True)
    container: dbc.Container = Field(init=False)

    default_width: str = Field(default='auto', kw_only=True)
    default_className: str = Field(
        default="mx-auto d-flex justify-content-center", kw_only=True
    )
    fluid: bool = Field(default=True, kw_only=True)

    component_ids: Dict[str, str] = Field(init=False, default_factory=dict)

    def create_init_layout(self):
        raise NotImplementedError(
            f"***{self.__class__.__name__} must implement `create_init_layout()` method***"
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        self.container = dbc.Container(
            children=self.create_init_layout(),
            id=self.container_id,
            className=self.default_className,
        )
