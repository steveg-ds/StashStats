import os
from unittest.mock import patch, MagicMock
import pytest
from stashies.ravelry_client import RavelryClient

# Set default env vars for tests to pass Pydantic settings checks
os.environ.setdefault("API_USERNAME", "test_user")
os.environ.setdefault("API_KEY", "test_key")
os.environ.setdefault("RAVELRY_USERNAME", "test_user")


def test_search_yarn_success():
    """Test search_yarn returns yarns list on successful response."""
    client = RavelryClient(api_username="test_user", api_key="test_key")
    mock_response_data = {
        "yarns": [
            {"id": 1, "name": "Super Soft Merino", "yarn_company": {"name": "Yarn Co"}},
            {"id": 2, "name": "Cozy Cotton", "yarn_company": {"name": "Cotton LLC"}},
        ]
    }
    
    with patch("stashies.base_req.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        results = client.search_yarn(query="merino", sort="best")

        assert results == mock_response_data["yarns"]
        mock_get.assert_called_once_with(
            "https://api.ravelry.com/yarns/search.json",
            auth=mock_get.call_args[1]["auth"],
            params={"query": "merino", "sort": "best"}
        )


def test_search_yarn_failure():
    """Test search_yarn returns None on failed response or error."""
    client = RavelryClient(api_username="test_user", api_key="test_key")
    with patch("stashies.base_req.requests.get") as mock_get:
        mock_get.side_effect = Exception("API connection timed out")
        
        results = client.search_yarn(query="silk")
        
        assert results is None


def test_get_yarn_success():
    """Test get_yarn returns yarn dictionary on successful response."""
    client = RavelryClient(api_username="test_user", api_key="test_key")
    mock_response_data = {
        "yarn": {"id": 42, "name": "Alpaca Blend", "yarn_company": {"name": "Warmth Co"}}
    }
    
    with patch("stashies.base_req.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = client.get_yarn(yarn_id=42)

        assert result == mock_response_data["yarn"]
        mock_get.assert_called_once_with(
            "https://api.ravelry.com/yarns/42.json",
            auth=mock_get.call_args[1]["auth"],
            params=None
        )


def test_get_yarn_failure():
    """Test get_yarn returns None on failed response or empty structure."""
    client = RavelryClient(api_username="test_user", api_key="test_key")
    with patch("stashies.base_req.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = client.get_yarn(yarn_id=999)

        assert result is None
