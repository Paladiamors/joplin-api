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
    List notes from Joplin with pagination.

    This tool retrieves a list of notes from the Joplin database. It returns metadata for each note,
    including the ID, title, creation/update timestamps, parent notebook ID, and todo status.
    The body of the note is NOT returned by this tool; use `get_note` for that.

    Args:
        limit: The maximum number of notes to return in a single request (default: 10).
        page: The page number to retrieve, starting from 1 (default: 1).

    Returns:
        A list of dictionaries, where each dictionary represents a note and contains:
        - id: The unique identifier of the note.
        - title: The title of the note.
        - updated_time: Timestamp of the last update.
        - created_time: Timestamp of creation.
        - parent_id: The ID of the notebook containing the note.
        - is_todo: 1 if the note is a todo, 0 otherwise.
        - todo_completed: Timestamp if completed, 0 otherwise.
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
    Retrieve the full content and metadata of a specific note.

    This tool fetches the complete details of a note, including its body content in Markdown format.
    Use this when you need to read the actual text of a note.

    Args:
        note_id: The unique identifier (ID) of the note to retrieve.

    Returns:
        A dictionary containing the note's details:
        - id: The unique identifier.
        - title: The title of the note.
        - body: The content of the note in Markdown.
        - updated_time: Timestamp of the last update.
        - created_time: Timestamp of creation.
        - parent_id: The ID of the notebook containing the note.
        - is_todo: 1 if the note is a todo, 0 otherwise.
        - todo_completed: Timestamp if completed, 0 otherwise.
    """
    params = {
        "fields": "id,title,body,updated_time,created_time,parent_id,is_todo,todo_completed"
    }
    return await _make_request("GET", f"/notes/{note_id}", params=params)

@mcp.tool()
async def create_note(title: str, body: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new note in Joplin.

    This tool creates a new note with the specified title and body content.
    You can optionally specify which notebook (folder) it should belong to.

    Args:
        title: The title of the new note.
        body: The body content of the note in Markdown format.
        parent_id: The ID of the notebook (folder) where the note should be created.
                   If not provided, it will be placed in the default notebook.

    Returns:
        A dictionary containing the metadata of the created note, including its new ID.
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
    Update an existing note's properties.

    Use this tool to change the title, body, or todo status of a note.
    Only the provided fields will be updated; others will remain unchanged.

    Args:
        note_id: The unique identifier of the note to update.
        title: The new title for the note (optional).
        body: The new Markdown body content for the note (optional).
        is_todo: Set to True to make this note a checkbox/todo item, or False to make it a regular note (optional).
        todo_completed: Set to True to mark the todo as completed, or False to mark it as uncompleted (optional).
                        This has no effect if the note is not a todo.

    Returns:
        A dictionary containing the updated properties of the note.
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

    This tool removes a note. By default, it moves the note to the trash (soft delete),
    allowing for recovery. You can optionally request a permanent deletion.

    Args:
        note_id: The unique identifier of the note to delete.
        permanent: If True, the note is permanently deleted and cannot be recovered.
                   If False (default), the note is moved to the trash.

    Returns:
        A dictionary containing the ID of the deleted note.
    """
    params = {}
    if permanent:
        params["permanent"] = "1"

    return await _make_request("DELETE", f"/notes/{note_id}", params=params)

@mcp.tool()
async def search_notes(query: str, limit: int = 10, page: int = 1) -> List[Dict[str, Any]]:
    """
    Search for notes using a query string.

    This tool performs a search across all notes in Joplin. It supports Joplin's search syntax.
    For example, you can search for keywords, tags, or other attributes.
    See https://joplinapp.org/help/apps/search/ for search syntax details.

    Args:
        query: The search query string (e.g., "grocery list", "tag:work").
        limit: The maximum number of results to return (default: 10).
        page: The page number to retrieve (default: 1).

    Returns:
        A list of matching notes (metadata only, no body), similar to `list_notes`.
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
async def list_folders(limit: int = 10, page: int = 1) -> List[Dict[str, Any]]:
    """
    List all notebooks (folders) in Joplin.

    This tool retrieves a list of notebooks, which can contain notes.
    Use the `id` from this list as the `parent_id` when creating or moving notes.

    Args:
        limit: The maximum number of folders to return (default: 10).
        page: The page number to retrieve (default: 1).

    Returns:
        A list of dictionaries, where each dictionary represents a notebook (folder) and contains:
        - id: The unique identifier of the folder.
        - title: The name of the folder.
        - updated_time: Timestamp of the last update.
        - created_time: Timestamp of creation.
        - parent_id: The ID of the parent folder (if nested), or empty if at the root.
    """
    params = {
        "limit": limit,
        "page": page,
        "fields": "id,title,updated_time,created_time,parent_id"
    }
    result = await _make_request("GET", "/folders", params=params)
    return result.get("items", [])

if __name__ == "__main__":
    mcp.run()
