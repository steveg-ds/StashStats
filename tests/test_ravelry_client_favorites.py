"""Unit tests for FavoritesMixin."""
import pytest
from unittest.mock import patch
from stashies.client.favorites import FavoritesMixin


class TestFavoritesMixin:
    """Tests for FavoritesMixin Ravelry API endpoints."""
    
    def test_get_favorites(self):
        """Test fetching favorites from API."""
        mock_response = {"favorites": [{"id": 1, "name": "Favorite Yarn"}]}
        
        with patch.object(FavoritesMixin, 'get_request', return_value=mock_response) as mock_get:
            mixin = FavoritesMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_favorites()
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["id"] == 1
            mock_get.assert_called_once_with("favorites/list.json")
    
    def test_get_favorites_empty(self):
        """Test empty favorites response."""
        with patch.object(FavoritesMixin, 'get_request', return_value={}) as mock_get:
            mixin = FavoritesMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_favorites()
            
            assert result is None
    
    def test_add_favorite(self):
        """Test adding item to favorites."""
        mock_response = {"favorite": {"id": 999, "name": "New Favorite"}}
        
        with patch.object(FavoritesMixin, 'post_request', return_value=mock_response) as mock_post:
            mixin = FavoritesMixin(api_username='test_user', api_key='test_key')
            result = mixin.add_favorite({"yarn_id": 123})
            
            assert result is not None
            assert result["id"] == 999
            mock_post.assert_called_once_with("favorites/add.json", json_data={"yarn_id": 123})
    
    def test_remove_favorite(self):
        """Test removing item from favorites."""
        with patch.object(FavoritesMixin, 'delete_request', return_value={}) as mock_delete:
            mixin = FavoritesMixin(api_username='test_user', api_key='test_key')
            result = mixin.remove_favorite(999)
            
            assert result is True
            mock_delete.assert_called_once_with("favorites/999.json")