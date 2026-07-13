"""Base client for Ravelry API requests."""
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any

class BaseRavelryClient:
    """
    Base client handling auth and raw requests.
    """

    def __init__(self, api_username: str, api_key: str, base_url: str = "https://api.ravelry.com"):
        self.api_username = api_username
        self.api_key = api_key
        self.base_url = base_url

    def get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_key),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def post_request(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        payload = json_data or data
        try:
            response = requests.post(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_key),
                json=payload,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def put_request(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        payload = json_data or data
        try:
            response = requests.put(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_key),
                json=payload,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def delete_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.delete(
                url,
                auth=HTTPBasicAuth(self.api_username, self.api_key),
                params=params
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception:
            return None
