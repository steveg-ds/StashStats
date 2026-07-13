import pytest
from unittest.mock import patch, MagicMock
from stashies.ravelry_client import RavelryClient

@pytest.fixture
def stash_client():
    return RavelryClient(api_username="test_user", api_key="test_key")

def test_get_stash_list_single_page(stash_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "unified_stash": [
            {"stash": {"id": 1, "name": "Yarn A"}}
        ]
    }
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        res = stash_client.get_stash_list("test_user")
        assert res == [{"stash": {"id": 1, "name": "Yarn A"}}]
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/people/test_user/stash/unified/list.json" in args[0]
        assert kwargs["params"] == {"page_size": 100, "page": 1}

def test_get_stash_list_multi_page(stash_client):
    mock_resp1 = MagicMock()
    mock_resp1.status_code = 200
    mock_resp1.json.return_value = {
        "unified_stash": [{"stash": {"id": i, "name": f"Yarn {i}"}} for i in range(100)]
    }
    
    mock_resp2 = MagicMock()
    mock_resp2.status_code = 200
    mock_resp2.json.return_value = {
        "unified_stash": [{"stash": {"id": 100, "name": "Yarn 100"}}]
    }
    
    with patch("requests.get", side_effect=[mock_resp1, mock_resp2]) as mock_get:
        res = stash_client.get_stash_list("test_user")
        assert len(res) == 101
        assert res[0]["stash"]["id"] == 0
        assert res[100]["stash"]["id"] == 100
        assert mock_get.call_count == 2

def test_get_stash_list_failure(stash_client):
    with patch("requests.get", side_effect=Exception("API error")):
        res = stash_client.get_stash_list("test_user")
        assert res is None

def test_create_stash_success(stash_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"stash": {"id": 123}}
    
    stash_data = {"name": "New Yarn", "skeins": 2}
    with patch("requests.post", return_value=mock_response) as mock_post:
        res = stash_client.create_stash("test_user", stash_data)
        assert res == {"stash": {"id": 123}}
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "/people/test_user/stash/create.json" in args[0]
        assert kwargs["json"] == stash_data

def test_update_stash_success(stash_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"stash": {"id": 123, "skeins": 3}}
    
    stash_data = {"skeins": 3}
    with patch("requests.put", return_value=mock_response) as mock_put:
        res = stash_client.update_stash("test_user", 123, stash_data)
        assert res == {"stash": {"id": 123, "skeins": 3}}
        mock_put.assert_called_once()
        args, kwargs = mock_put.call_args
        assert "/people/test_user/stash/123.json" in args[0]
        assert kwargs["json"] == stash_data

def test_delete_stash_success(stash_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"success": true}'
    mock_response.json.return_value = {"success": True}
    
    with patch("requests.delete", return_value=mock_response) as mock_delete:
        res = stash_client.delete_stash("test_user", 123, "yarn")
        assert res is True
        mock_delete.assert_called_once()
        args, kwargs = mock_delete.call_args
        assert "/people/test_user/stash/123.json" in args[0]
        assert kwargs["params"] == {"stash_type": "yarn"}

def test_delete_stash_failure(stash_client):
    with patch("requests.delete", side_effect=Exception("Delete failed")):
        res = stash_client.delete_stash("test_user", 123, "yarn")
        assert res is False
