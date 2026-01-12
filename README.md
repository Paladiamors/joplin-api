# Joplin MCP Server

This is a Model Context Protocol (MCP) server that connects to your local Joplin application. It allows AI assistants (like Claude Desktop or other MCP clients) to read, search, and create notes in your Joplin notebook.

## Features

- **List Notes**: Retrieve a list of notes with pagination. Includes metadata like todo status and update time.
- **Get Note**: Read the full content of a specific note, including todo status and update time.
- **Create Note**: Create new notes in Joplin.
- **Update Note**: Update note title, body, and todo completion status.
- **Delete Note**: Soft or permanently delete notes.
- **Search Notes**: Search for notes using Joplin's search functionality.
- **List Folders**: List all notebooks/folders with pagination.

## Prerequisites

- Python 3.10+
- Joplin Desktop Application running with the Web Clipper enabled.

## Installation

1. Clone this repository or download the files.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You need to get your Joplin Web Clipper Authorization Token:
1. Open Joplin.
2. Go to **Tools** > **Options** (or **Joplin** > **Preferences** on macOS).
3. Select **Web Clipper** in the sidebar.
4. Ensure the Web Clipper is enabled.
5. Copy the **Authorisation token**.

## Usage with MCP Clients

To use this server with an MCP client (like Claude Desktop), adds it to your `mcp.json` configuration file.

### Adding to `mcp.json`

Add the following entry to your `mcpServers` object in `mcp.json`. Replace `/path/to/your/python` with the path to your python executable (or just `python` if it's in your PATH) and `/path/to/joplin_mcp.py` with the absolute path to the script.

```json
{
  "mcpServers": {
    "joplin": {
      "command": "python",
      "args": [
        "/path/to/joplin_mcp.py"
      ],
      "env": {
        "JOPLIN_TOKEN": "YOUR_JOPLIN_AUTH_TOKEN_HERE",
        "JOPLIN_BASE_URL": "http://localhost:41184"
      }
    }
  }
}
```

> **Note**: `JOPLIN_BASE_URL` is optional and defaults to `http://localhost:41184`.

## Running Manually

You can also run the server manually for testing:

```bash
export JOPLIN_TOKEN=your_token
python joplin_mcp.py
```
