# Tests
These tests cover the MCP tools and providers layer.

## Install

```bash
python -m pip install -U pytest pytest-asyncio httpx
```

## Run

From your project root:

```bash
pytest
```

## Notes

- These tests assume your package layout matches your imports (`src/providers/`, `src/tools/`, `src/config/`).
- Network calls are mocked using `AsyncMock` from `unittest.mock`.
- Async functions are tested by wrapping tool calls with `asyncio.run()` or marking test functions with `@pytest.mark.asyncio`.
- Patch locations should match where functions are imported in the tool, not where they're defined (e.g., patch `src.tools.jira_tools.jira_get_issue.jira_api_get`, not `src.providers.jira.jira_api.jira_api_get`).
