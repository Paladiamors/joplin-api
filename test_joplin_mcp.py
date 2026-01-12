import unittest
from unittest.mock import patch, MagicMock
import joplin_mcp
import asyncio
import os
import time

class TestJoplinMCP(unittest.TestCase):
    def setUp(self):
        # Set environment variables for testing
        os.environ["JOPLIN_TOKEN"] = "test-token"
        os.environ["JOPLIN_BASE_URL"] = "http://localhost:41184"
        # Since JOPLIN_TOKEN is read at module level in joplin_mcp.py, we need to update it there
        joplin_mcp.JOPLIN_TOKEN = "test-token"
        joplin_mcp.JOPLIN_BASE_URL = "http://localhost:41184"

    def test_list_notes(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "items": [{"id": "1", "title": "Test Note"}],
                "has_more": False
            }

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            # Call the function
            result = asyncio.run(joplin_mcp.list_notes(limit=5, page=1))

            # Verify
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["title"], "Test Note")
            mock_request.assert_called_with(
                "GET",
                "http://localhost:41184/notes",
                params={"limit": 5, "page": 1, "fields": "id,title,updated_time,created_time,parent_id,is_todo,todo_completed", "token": "test-token"},
                json=None
            )

    def test_list_notes_in_folder(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "items": [{"id": "1", "title": "Folder Note"}],
                "has_more": False
            }

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            # Call the function
            result = asyncio.run(joplin_mcp.list_notes_in_folder(folder_id="folder123", limit=5, page=1))

            # Verify
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["title"], "Folder Note")
            mock_request.assert_called_with(
                "GET",
                "http://localhost:41184/folders/folder123/notes",
                params={"limit": 5, "page": 1, "fields": "id,title,updated_time,created_time,parent_id,is_todo,todo_completed", "token": "test-token"},
                json=None
            )

    def test_get_note(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"id": "1", "title": "Test Note", "body": "# Content"}

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            result = asyncio.run(joplin_mcp.get_note(note_id="1"))

            self.assertEqual(result["title"], "Test Note")
            self.assertEqual(result["body"], "# Content")
            mock_request.assert_called_with(
                "GET",
                "http://localhost:41184/notes/1",
                params={"fields": "id,title,body,updated_time,created_time,parent_id,is_todo,todo_completed", "token": "test-token"},
                json=None
            )

    def test_create_note(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"id": "2", "title": "New Note"}

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            result = asyncio.run(joplin_mcp.create_note(title="New Note", body="Body content"))

            self.assertEqual(result["id"], "2")
            mock_request.assert_called_with(
                "POST",
                "http://localhost:41184/notes",
                params={"token": "test-token"},
                json={"title": "New Note", "body": "Body content"}
            )

    def test_update_note(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"id": "1", "title": "Updated Title", "todo_completed": 123456789}

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            # Test updating title and marking as todo completed
            with patch("time.time", return_value=123456.789):
                result = asyncio.run(joplin_mcp.update_note(note_id="1", title="Updated Title", todo_completed=True))

            self.assertEqual(result["title"], "Updated Title")
            mock_request.assert_called_with(
                "PUT",
                "http://localhost:41184/notes/1",
                params={"token": "test-token"},
                json={"title": "Updated Title", "todo_completed": 123456789}
            )

    def test_delete_note(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"id": "1"}

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            # Test soft delete
            result = asyncio.run(joplin_mcp.delete_note(note_id="1"))
            mock_request.assert_called_with(
                "DELETE",
                "http://localhost:41184/notes/1",
                params={"token": "test-token"},
                json=None
            )

            # Test permanent delete
            result_perm = asyncio.run(joplin_mcp.delete_note(note_id="1", permanent=True))
            mock_request.assert_called_with(
                "DELETE",
                "http://localhost:41184/notes/1",
                params={"token": "test-token", "permanent": "1"},
                json=None
            )

    def test_search_notes(self):
         with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "items": [{"id": "3", "title": "Found Note"}],
                "has_more": False
            }

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            result = asyncio.run(joplin_mcp.search_notes(query="Found"))

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["title"], "Found Note")
            mock_request.assert_called_with(
                "GET",
                "http://localhost:41184/search",
                params={"query": "Found", "limit": 10, "page": 1, "fields": "id,title,updated_time,created_time,parent_id,is_todo,todo_completed", "token": "test-token"},
                json=None
            )

    def test_list_folders(self):
        with patch("httpx.AsyncClient.request") as mock_request:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "items": [{"id": "folder1", "title": "My Notebook"}],
                "has_more": False
            }

            async def return_mock_response(*args, **kwargs):
                return mock_response

            mock_request.side_effect = return_mock_response

            # Call the function
            result = asyncio.run(joplin_mcp.list_folders(limit=5, page=1))

            # Verify
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["title"], "My Notebook")
            mock_request.assert_called_with(
                "GET",
                "http://localhost:41184/folders",
                params={"limit": 5, "page": 1, "fields": "id,title,updated_time,created_time,parent_id", "token": "test-token"},
                json=None
            )

if __name__ == "__main__":
    unittest.main()
