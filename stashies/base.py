from pydantic import BaseModel
from typing import Any
from .utils import MODEL_CONFIG
from .utils import create_logger

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


class Base(BaseModel):
    """
    Base class for StashStats Pydantic dataclasses.

    - Methods:
        - __init_subclass__:
            - calls `create_logger` to assign a logger to child classes
    """

    model_config = MODEL_CONFIG

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Assign the logger to the class
        cls.LOGGER: "Logger" = create_logger(logger_name=cls.__name__)
