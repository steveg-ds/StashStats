"""Unit tests for YarnWeightsMixin."""
import pytest
from unittest.mock import patch
from stashies.client.yarn_weights import YarnWeightsMixin


class TestYarnWeightsMixin:
    """Tests for YarnWeightsMixin Ravelry API endpoints."""
    
    def test_get_yarn_weights(self):
        """Test fetching yarn weights from API."""
        mock_response = {"yarn_weights": [{"id": 1, "name": "Lace"}, {"id": 2, "name": "Bulky"}]}
        
        with patch.object(YarnWeightsMixin, 'get_request', return_value=mock_response) as mock_get:
            mixin = YarnWeightsMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_yarn_weights()
            
            assert result is not None
            assert len(result) == 2
            assert result[0]["name"] == "Lace"
            mock_get.assert_called_once_with("yarns/yarn_weights.json")
    
    def test_get_yarn_weights_empty(self):
        """Test empty yarn weights response."""
        with patch.object(YarnWeightsMixin, 'get_request', return_value={}) as mock_get:
            mixin = YarnWeightsMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_yarn_weights()
            
            assert result is None