"""Unit tests for QueueMixin."""
import pytest
from unittest.mock import MagicMock, patch
from stashies.client.queue import QueueMixin


class TestQueueMixin:
    """Tests for QueueMixin Ravelry API endpoints."""
    
    def test_get_queue(self):
        """Test fetching queue from API."""
        mock_response = {"queue": [{"id": 1, "name": "Test Project"}]}
        
        with patch.object(QueueMixin, 'get_request', return_value=mock_response) as mock_get:
            mixin = QueueMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_queue()
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["id"] == 1
            mock_get.assert_called_once_with("queue/list.json")
    
    def test_get_queue_empty(self):
        """Test empty queue response."""
        with patch.object(QueueMixin, 'get_request', return_value={}) as mock_get:
            mixin = QueueMixin(api_username='test_user', api_key='test_key')
            result = mixin.get_queue()
            
            assert result is None
    
    def test_add_to_queue(self):
        """Test adding item to queue."""
        mock_response = {"queue_item": {"id": 999, "name": "New Project"}}
        
        with patch.object(QueueMixin, 'post_request', return_value=mock_response) as mock_post:
            mixin = QueueMixin(api_username='test_user', api_key='test_key')
            result = mixin.add_to_queue({"pattern_id": 123})
            
            assert result is not None
            assert result["id"] == 999
            mock_post.assert_called_once_with("queue/add.json", json_data={"pattern_id": 123})
    
    def test_remove_from_queue(self):
        """Test removing item from queue."""
        with patch.object(QueueMixin, 'delete_request', return_value={}) as mock_delete:
            mixin = QueueMixin(api_username='test_user', api_key='test_key')
            result = mixin.remove_from_queue(999)
            
            assert result is True
            mock_delete.assert_called_once_with("queue/999.json")