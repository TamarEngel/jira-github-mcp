# Architecture
This document describes the high-level architecture of the MCP GitHub & Jira integration.

## System Diagram

```mermaid
graph TD
    MCP["MCP Server<br/>(FastMCP Framework)"]
    
    MCP --> GHTools["GitHub Tools"]
    MCP --> JiraTools["Jira Tools"]
    
    GHTools --> GHT1["create_branch"]
    GHTools --> GHT2["commit_and_push"]
    GHTools --> GHT3["create_pr"]
    GHTools --> GHT4["merge_pr"]
    
    JiraTools --> JT1["get_issue"]
    JiraTools --> JT2["search_issues"]
    JiraTools --> JT3["get_my_issues"]
    JiraTools --> JT4["transition_issue"]
    
    GHT1 --> GHAPI["GitHub API<br/>(httpx.Async)"]
    GHT2 --> GHAPI
    GHT3 --> GHAPI
    GHT4 --> GHAPI
    
    JT1 --> JiraAPI["Jira API<br/>(httpx.Async)"]
    JT2 --> JiraAPI
    JT3 --> JiraAPI
    JT4 --> JiraAPI
    
    GHAPI --> GHREST["GitHub REST API<br/>(github.com)"]
    JiraAPI --> JiraREST["Jira REST API<br/>(atlassian.net)"]
```

## Component Flow

### 1. Tool Registration Layer
Each tool is registered with the MCP server via the `@mcp.tool()` decorator.

```
User Request
    ↓
MCP Server receives tool call
    ↓
Route to registered tool function
    ↓
Execute async tool function
    ↓
Return result to user
```

### 2. Tool Layer (src/tools/)
Tools orchestrate the workflow:
- Accept user parameters
- Validate inputs
- Call provider APIs
- Format and return results

Example: `github_create_branch`
```
Input: issue_key, branch_name (optional)
    ↓
Get repo config (extract owner/repo)
    ↓
Fetch base branch SHA (github_api_get)
    ↓
Create new branch (github_api_post)
    ↓
Return: branch ref + commit SHA
```

### 3. Provider Layer (src/providers/)
Low-level API clients for GitHub & Jira:

**GitHub Provider:**
- `github_api_get()` - GET requests with auth headers
- `github_api_post()` - POST requests with JSON body
- `github_api_put()` - PUT requests for merges
- Uses `httpx.AsyncClient` for async HTTP

**Jira Provider:**
- `jira_api_get()` - GET requests with Basic Auth
- `jira_api_post()` - POST requests (search, transitions)
- Uses `httpx.AsyncClient` for async HTTP

### 4. Config Layer (src/config/)
Load and validate environment variables:
- `github_config.py` - GITHUB_REPO_URL, GITHUB_TOKEN, GITHUB_DEFAULT_BRANCH
- `jira_config.py` - JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
- Provide helper functions like `extract_repo_info()`

## Async Flow

All providers use async I/O with `httpx.AsyncClient`:

```
Tool calls: await github_api_get(...)
    ↓
Provider function awaits httpx response
    ↓
HTTP request sent (non-blocking)
    ↓
Response received
    ↓
Tool processes result
    ↓
Return to MCP Server
```

Benefits:
- Multiple concurrent requests don't block
- Better resource utilization
- Faster response times for parallel operations

## Testing Strategy

Tests use mocking to avoid real API calls:

```
Test calls: asyncio.run(tool(...))
    ↓
Tool code runs with mocked providers
    ↓
Mocks return predefined responses (AsyncMock)
    ↓
Assertions verify tool called API correctly
    ↓
No network traffic, fast & repeatable
```

Key mocking pattern:
```python
with patch('src.tools.jira_tools.jira_get_issue.jira_api_get', 
           new=AsyncMock(return_value={"key": "KAN-1"})):
    result = asyncio.run(tool("KAN-1"))
    # Assert mock was called with correct params
```

## Error Handling

Tools validate and provide clear error messages:

- **Config errors** → ValueError (missing env vars)
- **API errors** → ValueError (404, 422, etc.)
- **Merge conflicts** → ValueError (PR not mergeable)
- **Validation errors** → ValueError (invalid transitions, missing reviews)
