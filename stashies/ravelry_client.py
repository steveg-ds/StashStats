"""Ravelry API client implementation."""
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any

class RavelryClient:
    """
    Client for interacting with the Ravelry API.
    """

    def __init__(self, api_username: str, api_key: str, base_url: str = "https://api.ravelry.com"):
        """
        Initialize the RavelryClient.

        Args:
            api_username (str): The username for API authentication.
            api_key (str): The API key for authentication.
            base_url (str, optional): The base URL of the Ravelry API. Defaults to "https://api.ravelry.com".
        """
        self.api_username = api_username
        self.api_key = api_key
        self.base_url = base_url

    def get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Perform a GET request to the Ravelry API.

        Args:
            endpoint (str): The endpoint path (e.g., 'current_user.json').
            params (dict, optional): URL query parameters.

        Returns:
            dict or None: The parsed JSON response, or None on error.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_key),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None
