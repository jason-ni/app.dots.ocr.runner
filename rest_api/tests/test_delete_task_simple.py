"""
Simple tests for the updated delete_task behavior that only allows deletion of completed tasks.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from dotsocr_runner_client import (
    DotsOCRRunnerClient, AsyncDotsOCRRunnerClient, TaskNotCompletedError, TaskNotFoundError
)
from dotsocr_runner_client.models import TaskStatusResponse, DeleteResponse


class TestDeleteTaskSimple:
    """Simple test cases for the updated delete_task behavior."""

    def test_sync_delete_completed_task_success(self):
        """Test successful deletion of a completed task."""
        client = DotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock the task status check to return completed
        mock_status = TaskStatusResponse(
            task_id="test-task-id",
            status="completed",
            progress=100.0,
            filename="test.pdf"
        )
        
        # Mock the delete response
        mock_delete_response = DeleteResponse(
            task_id="test-task-id",
            status="deleted"
        )
        
        with patch.object(client, 'get_task_status', return_value=mock_status), \
             patch.object(client, '_make_request') as mock_request:
            
            mock_request.return_value.json.return_value = {
                'task_id': 'test-task-id',
                'status': 'deleted',
                'files_removed': True,
                'repository_cleaned': False
            }
            
            result = client.delete_task("test-task-id")
            
            assert result.task_id == "test-task-id"
            assert result.status == "deleted"

    def test_sync_delete_pending_task_raises_error(self):
        """Test that deleting a pending task raises TaskNotCompletedError."""
        client = DotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock the task status check to return pending
        mock_status = TaskStatusResponse(
            task_id="test-task-id",
            status="pending",
            progress=0.0,
            filename="test.pdf"
        )
        
        with patch.object(client, 'get_task_status', return_value=mock_status):
            with pytest.raises(TaskNotCompletedError) as exc_info:
                client.delete_task("test-task-id")
            
            assert "test-task-id" in str(exc_info.value)
            assert "Only completed tasks can be deleted" in str(exc_info.value)
            assert "pending" in str(exc_info.value)

    def test_sync_delete_running_task_raises_error(self):
        """Test that deleting a running task raises TaskNotCompletedError."""
        client = DotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock the task status check to return running
        mock_status = TaskStatusResponse(
            task_id="test-task-id",
            status="running",
            progress=50.0,
            filename="test.pdf"
        )
        
        with patch.object(client, 'get_task_status', return_value=mock_status):
            with pytest.raises(TaskNotCompletedError) as exc_info:
                client.delete_task("test-task-id")
            
            assert "test-task-id" in str(exc_info.value)
            assert "Only completed tasks can be deleted" in str(exc_info.value)
            assert "running" in str(exc_info.value)

    def test_sync_delete_failed_task_raises_error(self):
        """Test that deleting a failed task raises TaskNotCompletedError."""
        client = DotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock the task status check to return failed
        mock_status = TaskStatusResponse(
            task_id="test-task-id",
            status="failed",
            progress=0.0,
            filename="test.pdf"
        )
        
        with patch.object(client, 'get_task_status', return_value=mock_status):
            with pytest.raises(TaskNotCompletedError) as exc_info:
                client.delete_task("test-task-id")
            
            assert "test-task-id" in str(exc_info.value)
            assert "Only completed tasks can be deleted" in str(exc_info.value)
            assert "failed" in str(exc_info.value)

    def test_sync_delete_nonexistent_task_propagates_error(self):
        """Test that deleting a non-existent task propagates TaskNotFoundError."""
        client = DotsOCRRunnerClient("http://test.com", "test-token")
        
        with patch.object(client, 'get_task_status', side_effect=TaskNotFoundError("Task not found")):
            with pytest.raises(TaskNotFoundError):
                client.delete_task("nonexistent-task-id")

    @pytest.mark.asyncio
    async def test_async_delete_completed_task_success(self):
        """Test successful deletion of a completed task using async client."""
        client = AsyncDotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock the task status check to return completed
        mock_status = TaskStatusResponse(
            task_id="test-task-id",
            status="completed",
            progress=100.0,
            filename="test.pdf"
        )
        
        # Mock the delete response
        mock_delete_response = {
            'task_id': 'test-task-id',
            'status': 'deleted',
            'files_removed': True,
            'repository_cleaned': False
        }
        
        with patch.object(client, 'get_task_status', new_callable=AsyncMock, return_value=mock_status), \
             patch.object(client, '_make_request', new_callable=AsyncMock, return_value=mock_delete_response):
            
            result = await client.delete_task("test-task-id")
            
            assert result.task_id == "test-task-id"
            assert result.status == "deleted"

    @pytest.mark.asyncio
    async def test_async_delete_pending_task_raises_error(self):
        """Test that deleting a pending task raises TaskNotCompletedError using async client."""
        client = AsyncDotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock the task status check to return pending
        mock_status = TaskStatusResponse(
            task_id="test-task-id",
            status="pending",
            progress=0.0,
            filename="test.pdf"
        )
        
        with patch.object(client, 'get_task_status', new_callable=AsyncMock, return_value=mock_status):
            with pytest.raises(TaskNotCompletedError) as exc_info:
                await client.delete_task("test-task-id")
            
            assert "test-task-id" in str(exc_info.value)
            assert "Only completed tasks can be deleted" in str(exc_info.value)
            assert "pending" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_delete_nonexistent_task_propagates_error(self):
        """Test that deleting a non-existent task propagates TaskNotFoundError using async client."""
        client = AsyncDotsOCRRunnerClient("http://test.com", "test-token")
        
        with patch.object(client, 'get_task_status', new_callable=AsyncMock, side_effect=TaskNotFoundError("Task not found")):
            with pytest.raises(TaskNotFoundError):
                await client.delete_task("nonexistent-task-id")

    def test_delete_task_status_check_error_handling(self):
        """Test error handling when status check fails for other reasons."""
        client = DotsOCRRunnerClient("http://test.com", "test-token")
        
        # Mock a different API error during status check
        with patch.object(client, 'get_task_status', side_effect=Exception("Connection error")):
            with pytest.raises(Exception, match="Connection error"):
                client.delete_task("test-task-id")


if __name__ == "__main__":
    pytest.main([__file__])
