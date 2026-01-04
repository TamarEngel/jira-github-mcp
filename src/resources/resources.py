"""
MCP Resources
Static resources that Copilot can always access
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path


def _load_resource(filename: str) -> str:
    """Load markdown file with relative path"""
    path = Path(__file__).parent / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"# {filename} Not Found"


def register(mcp: FastMCP) -> None:
    """Register all resources with FastMCP"""
    
    @mcp.resource(uri="guide://workflow")
    def workflow_guide() -> str:
        """Development workflow guide"""
        return _load_resource("workflow_guide.md")
    
    @mcp.resource(uri="docs://api")
    def api_reference() -> str:
        """API reference for all tools"""
        return _load_resource("api_reference.md")
    
    @mcp.resource(uri="issue://current")
    def current_issue() -> str:
        """Current issue being worked on"""
        return _load_resource("current_issue.md")
