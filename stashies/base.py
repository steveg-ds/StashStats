from typing import Any
from .utils import create_logger

from logging import Logger


class Base:
    """
    Base class for StashStats Pydantic dataclasses.

    - Methods:
        - __init_subclass__:
            - calls `create_logger` to assign a logger to child classes
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Assign the logger to the class
        cls.LOGGER: 'Logger' = create_logger(logger_name=cls.__name__)
        '''Provides a logger object to child classes via self.LOGGER '''
