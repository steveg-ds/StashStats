"""Unit tests for ColorFamiliesMixin."""
import pytest
from unittest.mock import patch
from stashies.client.color_families import ColorFamiliesMixin


class TestColorFamiliesMixin:
    """Tests for ColorFamiliesMixin Ravelry API endpoints."""
    
    def test_get_color_families(self):
        """Test fetching color families from API."""
        mock_response = {"color_families": [{"id": 1, "name": "Red"}, {"id": 2, "name": "Blue"}]}
        
        with patch.object(ColorFamiliesMixin, 'get_request', return_value=mock_response) as mock_get:
            mixin = ColorFamiliesMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_color_families()
            
            assert result is not None
            assert len(result) == 2
            assert result[0]["name"] == "Red"
            mock_get.assert_called_once_with("yarns/color_families.json")
    
    def test_get_color_families_empty(self):
        """Test empty color families response."""
        with patch.object(ColorFamiliesMixin, 'get_request', return_value={}) as mock_get:
            mixin = ColorFamiliesMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_color_families()
            
            assert result is None