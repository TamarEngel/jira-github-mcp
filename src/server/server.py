"""
MCP Server Module

Initializes and runs the Jira-GitHub MCP (Model Context Protocol) server.
Registers all tools, resources, and prompts that enable end-to-end workflow automation
for Jira issue management and GitHub repository operations.
"""

from mcp.server.fastmcp import FastMCP
from src.tools.jira_tools.jira_get_issue import register as reg_get_issue
from src.tools.jira_tools.jira_search_issues import register as reg_search
from src.tools.jira_tools.jira_get_my_issues import register as reg_my_issues
from src.tools.jira_tools.jira_transition_issue import register as reg_transition
from src.tools.github_tools.github_create_branch import register as reg_github_create_branch
from src.tools.github_tools.github_create_pull_request import register as reg_github_create_pr
from src.tools.github_tools.github_commit_and_push import register as reg_github_commit_push
from src.tools.github_tools.github_merge_pr import register as reg_github_merge_pr
from src.prompts.dev_workflow import register as reg_workflow_prompts
from src.resources.resources import register as reg_resources

def register_tools(mcp: FastMCP) -> None:
    """
    Register all Jira and GitHub tools on the MCP server.
    Each module exposes a register(mcp) function that attaches a tool to the server.
    
    This function wires domain-specific tools into the MCP runtime,
    enabling end-to-end issue and repository workflows.
    """
    # Jira tools
    reg_get_issue(mcp)
    reg_search(mcp)
    reg_my_issues(mcp)
    reg_transition(mcp)
    
    # GitHub tools
    reg_github_create_branch(mcp)
    reg_github_create_pr(mcp)
    reg_github_commit_push(mcp)
    reg_github_merge_pr(mcp)
    
def register_resources(mcp: FastMCP) -> None:
    """
    Register MCP resources.

    Resources provide static context and reference material
    that help guide the LLM during tool usage.
    """
    reg_resources(mcp)

def register_prompts(mcp: FastMCP) -> None:
    """
    Register MCP prompts.

    Prompts define guided workflows and best practices that help
    the LLM orchestrate tools correctly and consistently.
    """
    reg_workflow_prompts(mcp)

def main() -> None:
    """Entry point: build and run the Jira-GitHub MCP server."""
    mcp = FastMCP("jira-github-mcp")
    
    # Register core capabilities first, then add guidance/context for the LLM.
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    mcp.run()

if __name__ == "__main__":
    main()

