"""
--- base_req.py ---
provides basic methods for interacting with the Ravelry API
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from typing import Union, Dict, Any, ClassVar
from .base import Base


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

    def get_request(self, endpoint: str) -> Union[Dict[str, Any], None]:
        """
        Function for making requests to Ravelry API.
        - Input
            - endpoint: end of API query e.x.`current_user.json`
        - output: Data returned from API
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(
                url, auth=HTTPBasicAuth(self.API_USERNAME, self.API_KEY)
            )
            response.raise_for_status()
        except HTTPError as http_err:
            self.LOGGER.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.LOGGER.error(f"Other error occurred: {err}")
        else:
            self.LOGGER.info(response.json())
            return response.json()

        return None

    def post_request(self) -> None:
        self.LOGGER.error("Method not implemented")
        pass


if __name__ == "main":

    x = Req()
    x.get_request(endpoint="current_user.json")
