"""
--- base_req.py ---
provides basic methods for interacting with the Ravelry API
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from typing import Optional, Dict, Any, ClassVar
from pydantic.dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from .base import Base


@dataclass
class Req(Base):
    """
    Base class for making Ravelry API Requests

    - Properties:
        - API_USERNAME (ClassVar[str]): Username for HTTPBasicAuth.
        - API_KEY (ClassVar[str]): API key for HTTPBasicAuth.
    - Methods:
        - get_request:
            - parameters:
                - endpoint (str): Endpoint for the url to be requested.
    """

    load_dotenv()

    API_USERNAME: ClassVar[str] = os.getenv("API_USERNAME") or ""
    API_KEY: ClassVar[str] = os.getenv("API_KEY") or ""

    BASE_URL: str = "https://api.ravelry.com"

    def get_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Function for making requests to Ravelry API.
        - Input
            - endpoint: end of API query e.x.`current_user.json`
        - output: Data returned from API
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(
                url, auth=HTTPBasicAuth(self.API_USERNAME, self.API_KEY), params=params
            )
            response.raise_for_status()
        except HTTPError as http_err:
            self.LOGGER.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.LOGGER.error(f"Other error occurred: {err}")
        else:
            return dict(response.json())

        return None
