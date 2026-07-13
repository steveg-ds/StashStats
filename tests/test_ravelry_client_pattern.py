import pytest
from unittest.mock import patch, MagicMock
from stashies.ravelry_client import RavelryClient

@patch("requests.get")
def test_search_patterns_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "patterns": [
            {
                "id": 101,
                "name": "Super Hat",
                "permalink": "super-hat",
                "designer": {"name": "Alice Designer"},
                "free": True
            }
        ]
    }
    mock_get.return_value = mock_response

    client = RavelryClient(api_username="test_user", api_key="test_key")
    res = client.search_patterns("super")

    assert res == [
        {
            "id": 101,
            "name": "Super Hat",
            "permalink": "super-hat",
            "designer": {"name": "Alice Designer"},
            "free": True
        }
    ]
    mock_get.assert_called_once_with(
        "https://api.ravelry.com/patterns/search.json",
        auth=mock_get.call_args[1]["auth"],
        params={"query": "super"}
    )

@patch("requests.get")
def test_get_pattern_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "pattern": {
            "id": 101,
            "name": "Super Hat",
            "permalink": "super-hat",
            "designer": {"name": "Alice Designer"},
            "free": True
        }
    }
    mock_get.return_value = mock_response

    client = RavelryClient(api_username="test_user", api_key="test_key")
    res = client.get_pattern(101)

    assert res == {
        "id": 101,
        "name": "Super Hat",
        "permalink": "super-hat",
        "designer": {"name": "Alice Designer"},
        "free": True
    }
    mock_get.assert_called_once_with(
        "https://api.ravelry.com/patterns/101.json",
        auth=mock_get.call_args[1]["auth"],
        params=None
    )

@patch("requests.get")
def test_search_patterns_failure(mock_get):
    mock_get.side_effect = Exception("API down")

    client = RavelryClient(api_username="test_user", api_key="test_key")
    res = client.search_patterns("super")

    assert res is None

@patch("requests.get")
def test_get_pattern_failure(mock_get):
    mock_get.side_effect = Exception("API down")

    client = RavelryClient(api_username="test_user", api_key="test_key")
    res = client.get_pattern(101)

    assert res is None
