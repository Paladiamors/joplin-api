from mcp.server.fastmcp import FastMCP
import httpx
import os
import time
from typing import Optional, List, Dict, Any

# Configuration
JOPLIN_BASE_URL = os.getenv("JOPLIN_BASE_URL", "http://localhost:41184")
JOPLIN_TOKEN = os.getenv("JOPLIN_TOKEN")

mcp = FastMCP("Joplin MCP Server")

async def _make_request(method: str, endpoint: str, params: Optional[Dict] = None, json: Optional[Dict] = None) -> Any:
    """Helper function to make requests to the Joplin API."""
    if not JOPLIN_TOKEN:
        raise ValueError("JOPLIN_TOKEN environment variable is not set.")

    url = f"{JOPLIN_BASE_URL}{endpoint}"
    params = params or {}
    params["token"] = JOPLIN_TOKEN

    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, params=params, json=json)
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def list_notes(limit: int = 10, page: int = 1) -> List[Dict[str, Any]]:
    """
    List notes from Joplin.

    Args:
        limit: Number of notes to return (default 10).
        page: Page number (default 1).
    """
    params = {
        "limit": limit,
        "page": page,
        "fields": "id,title,updated_time,created_time,parent_id,is_todo,todo_completed"
    }
    result = await _make_request("GET", "/notes", params=params)
    return result.get("items", [])

@mcp.tool()
async def get_note(note_id: str) -> Dict[str, Any]:
    """
    Get a specific note by ID.

    Args:
        note_id: The ID of the note to retrieve.
    """
    params = {
        "fields": "id,title,body,updated_time,created_time,parent_id,is_todo,todo_completed"
    }
    return await _make_request("GET", f"/notes/{note_id}", params=params)

@mcp.tool()
async def create_note(title: str, body: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new note in Joplin.

    Args:
        title: The title of the note.
        body: The body of the note (Markdown).
        parent_id: Optional ID of the notebook (folder) to place the note in.
    """
    data = {
        "title": title,
        "body": body
    }
    if parent_id:
        data["parent_id"] = parent_id

    return await _make_request("POST", "/notes", json=data)

@mcp.tool()
async def update_note(note_id: str, title: Optional[str] = None, body: Optional[str] = None, is_todo: Optional[bool] = None, todo_completed: Optional[bool] = None) -> Dict[str, Any]:
    """
    Update a note in Joplin.

    Args:
        note_id: The ID of the note to update.
        title: The new title (optional).
        body: The new body (optional).
        is_todo: Set whether this is a todo (optional).
        todo_completed: Set todo completion status (True for completed, False for uncompleted).
    """
    data = {}
    if title is not None:
        data["title"] = title
    if body is not None:
        data["body"] = body
    if is_todo is not None:
        data["is_todo"] = 1 if is_todo else 0
    if todo_completed is not None:
        if todo_completed:
            data["todo_completed"] = int(time.time() * 1000)
        else:
            data["todo_completed"] = 0

    return await _make_request("PUT", f"/notes/{note_id}", json=data)

@mcp.tool()
async def delete_note(note_id: str, permanent: bool = False) -> Dict[str, Any]:
    """
    Delete a note from Joplin.

    Args:
        note_id: The ID of the note to delete.
        permanent: If True, permanently deletes the note. If False (default), moves to trash.
    """
    params = {}
    if permanent:
        params["permanent"] = "1"

    return await _make_request("DELETE", f"/notes/{note_id}", params=params)

@mcp.tool()
async def search_notes(query: str, limit: int = 10, page: int = 1) -> List[Dict[str, Any]]:
    """
    Search for notes in Joplin.

    Args:
        query: The search query.
        limit: Number of results to return.
        page: Page number.
    """
    params = {
        "query": query,
        "limit": limit,
        "page": page,
        "fields": "id,title,updated_time,created_time,parent_id,is_todo,todo_completed"
    }
    result = await _make_request("GET", "/search", params=params)
    return result.get("items", [])

@mcp.tool()
async def list_folders() -> List[Dict[str, Any]]:
    """
    List all folders (notebooks).
    """
    result = await _make_request("GET", "/folders")
    return result.get("items", [])

if __name__ == "__main__":
    mcp.run()
