"""Abstract base class for all StashStats Dash UI components."""
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Dict, Any
import dash_bootstrap_components as dbc

from ..utils import MODEL_CONFIG


@dataclass
class BaseComponent:
    """
    Abstract base for Dash layout components.
    Subclasses must implement `create_init_layout()` and call `super().__post_init__()` to build the container.

    - Properties:
        - container_id (str): Dash element ID for the outer dbc.Container.
        - container (dbc.Container): Rendered container; built in __post_init__.
        - default_width (str): Bootstrap column width. Defaults to 'auto'.
        - default_className (str): CSS classes on the container.
        - fluid (bool): Whether the container spans full width.
        - component_ids (dict): Registry of child component IDs, populated by subclasses.
    - Methods:
        - create_init_layout: Abstract — build and return initial layout children.
        - __post_init__: Constructs dbc.Container from create_init_layout output.
    """
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
        """
        Build and return the initial layout children for this component.
        Must be implemented by every subclass.
        - output: Dash layout element(s) to render inside the container.
        """
        raise NotImplementedError(
            f"***{self.__class__.__name__} must implement `create_init_layout()` method***"
        )

    def __post_init__(self, *args: Any, **kwargs: Any):
        """
        Pydantic post-init hook. Constructs self.container from create_init_layout().
        """
        self.container = dbc.Container(
            children=self.create_init_layout(),
            id=self.container_id,
            className=self.default_className,
        )
