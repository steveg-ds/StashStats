import pytest
from unittest.mock import patch, MagicMock
from stashies.ravelry_client import RavelryClient

def test_ravelry_client_init():
    client = RavelryClient(api_username="test_user", api_key="test_key")
    assert client.api_username == "test_user"
    assert client.api_key == "test_key"
    assert client.base_url == "https://api.ravelry.com"

@patch("requests.get")
def test_ravelry_client_get_request(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_get.return_value = mock_response

    client = RavelryClient(api_username="test", api_key="key")
    res = client.get_request("current_user.json")
    
    assert res == {"status": "ok"}
    mock_get.assert_called_once()
    
    args, kwargs = mock_get.call_args
    assert kwargs["auth"] is not None
