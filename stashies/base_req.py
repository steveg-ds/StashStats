"""HTTP request base class for authenticated Ravelry API calls."""
import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from typing import Optional, Dict, Any, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict

from stashies import Base

class Req(Base, BaseSettings):
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
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    BASE_URL: ClassVar[str] = "https://api.ravelry.com"

    API_USERNAME: str
    API_KEY: str


    def put_request(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Function for making PUT requests to Ravelry API.
        - Input
            - endpoint (str): API endpoint path e.g. `people/username/stash/123.json`.
            - data (dict | None): JSON body payload.
            - params (dict | None): URL query parameters.
        - output: Response JSON as dict, or None on error.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.put(
                url,
                auth=HTTPBasicAuth(self.API_USERNAME, self.API_KEY),
                json=data,
                params=params
            )
            response.raise_for_status()
        except HTTPError as http_err:
            self.LOGGER.error(f"HTTP error occurred: {http_err}")
            if response is not None:
                self.LOGGER.error(f"Response content: {response.text}")
        except Exception as err:
            self.LOGGER.error(f"Other error occurred: {err}")
        else:
            return dict(response.json())

        return None

    def post_request(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Function for making POST requests to Ravelry API.
        - Input
            - endpoint (str): API endpoint path e.g. `people/username/stash/create.json`.
            - data (dict | None): JSON body payload.
            - params (dict | None): URL query parameters.
        - output: Response JSON as dict, or None on error.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.post(
                url, 
                auth=HTTPBasicAuth(self.API_USERNAME, self.API_KEY), 
                json=data,
                params=params
            )
            response.raise_for_status()
        except HTTPError as http_err:
            self.LOGGER.error(f"HTTP error occurred: {http_err}")
            if response is not None:
                self.LOGGER.error(f"Response content: {response.text}")
        except Exception as err:
            self.LOGGER.error(f"Other error occurred: {err}")
        else:
            return dict(response.json())

        return None


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