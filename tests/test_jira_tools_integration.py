"""Integration tests for Jira Tools
Tests that each tool calls the provider with correct endpoints and parameters.
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.tools.jira_tools.jira_get_issue import register as register_get_issue
from src.tools.jira_tools.jira_search_issues import register as register_search_issues
from src.tools.jira_tools.jira_get_my_issues import register as register_my_issues
from src.tools.jira_tools.jira_transition_issue import register as register_transition


class MockFastMCP:
    """Mock FastMCP to extract registered tool functions."""
    def __init__(self):
        self.tools = {}
    
    def tool(self, name):
        def decorator(func):
            self.tools[name] = func
            return func
        return decorator


def get_tool_function(register_func, tool_name):
    """Extract tool function from register function"""
    mcp = MockFastMCP()
    register_func(mcp)
    return mcp.tools[tool_name]


class TestJiraGetIssueTool:
    """Tests jira_get_issue calls provider correctly"""
    
    @pytest.mark.parametrize("fields", [None, ["created", "updated"]])
    def test_get_issue(self, fields):
        """Tool builds correct endpoint and applies parameters"""
        with patch('src.tools.jira_tools.jira_get_issue.jira_api_get', new=AsyncMock(return_value={"key": "KAN-15", "fields": {}})) as mock_get:
            with patch('src.tools.jira_tools.jira_get_issue.format_issue', return_value={"key": "KAN-15"}) as mock_format:
                tool = get_tool_function(register_get_issue, "jira_get_issue")
                result = asyncio.run(tool("KAN-15", fields=fields) if fields else tool("KAN-15"))
                
                # Verify endpoint
                mock_get.assert_called_once()
                assert mock_get.call_args.args[0] == "/issue/KAN-15"
                
                # Verify fields parameter if provided
                if fields:
                    params = mock_get.call_args.kwargs.get("params", {})
                    assert all(f in params.get("fields", "") for f in fields)
    
    def test_propagates_provider_error(self):
        """Tool propagates error when provider fails"""
        with patch('src.tools.jira_tools.jira_get_issue.jira_api_get', new=AsyncMock(side_effect=Exception("404: Issue not found"))):
            tool = get_tool_function(register_get_issue, "jira_get_issue")
            
            with pytest.raises(Exception) as exc_info:
                asyncio.run(tool("INVALID-999"))
            assert "404" in str(exc_info.value)


class TestJiraSearchIssuesTool:
    """Tests jira_search_issues builds correct JQL and calls provider"""
    
    @pytest.mark.parametrize("jql,max_results,fields", [
        ("project = KAN", 20, None),
        ("project = TEST", 10, ["customfield_1000"]),
    ])
    def test_search_issues(self, jql, max_results, fields):
        """Tool builds JQL with parameters and optional fields"""
        with patch('src.tools.jira_tools.jira_search_issues.jira_api_post', new=AsyncMock(return_value={"issues": [{"key": "KAN-1"}], "total": 1})) as mock_post:
            with patch('src.tools.jira_tools.jira_search_issues.format_issues_list', return_value={"issues": [{"key": "KAN-1"}], "total": 1}) as mock_format:
                tool = get_tool_function(register_search_issues, "jira_search_issues")
                result = asyncio.run(tool(jql, max_results=max_results, fields=fields) if fields else tool(jql, max_results=max_results))
                
                # Verify endpoint
                mock_post.assert_called_once()
                assert mock_post.call_args.args[0] == "/search/jql"
                
                # Verify request body
                json_body = mock_post.call_args.kwargs["json_body"]
                assert json_body["jql"] == jql
                assert json_body["maxResults"] == max_results
                
                if fields:
                    assert "customfield_1000" in json_body["fields"]


class TestJiraGetMyIssuesTool:
    """Tests jira_get_my_issues queries with currentUser() filter"""
    
    @pytest.mark.parametrize("status,issue_type", [
        (None, None),
        ("In Progress", None),
        ("Done", "Bug"),
    ])
    def test_get_my_issues(self, status, issue_type):
        """Tool builds JQL with currentUser() and optional filters"""
        with patch('src.tools.jira_tools.jira_get_my_issues.jira_api_post', new=AsyncMock(return_value={"issues": [], "total": 0})) as mock_post:
            with patch('src.tools.jira_tools.jira_get_my_issues.format_issues_list', return_value={"issues": [], "total": 0}) as mock_format:
                tool = get_tool_function(register_my_issues, "jira_get_my_issues")
                kwargs = {}
                if status:
                    kwargs["status"] = status
                if issue_type:
                    kwargs["issue_type"] = issue_type
                result = asyncio.run(tool(**kwargs))
                
                # Verify JQL contains currentUser
                json_body = mock_post.call_args.kwargs["json_body"]
                assert "currentUser()" in json_body["jql"]
                
                if status:
                    assert status in json_body["jql"]
                if issue_type:
                    assert issue_type in json_body["jql"]


class TestJiraTransitionIssueTool:
    """Tests jira_transition_issue sends correct transition request"""
    
    @pytest.mark.parametrize("status,comment", [
        ("In Progress", None),
        ("Done", "Task completed successfully"),
    ])
    def test_transition_issue(self, status, comment):
        """Tool transitions issue with optional comment"""
        with patch('src.tools.jira_tools.jira_transition_issue.jira_api_get', new=AsyncMock(return_value={
            "transitions": [
                {"id": "11", "name": "Start Progress", "to": {"name": "In Progress"}},
                {"id": "21", "name": "Done", "to": {"name": "Done"}}
            ]
        })) as mock_get:
            with patch('src.tools.jira_tools.jira_transition_issue.jira_api_post', new=AsyncMock(return_value={"success": True})) as mock_post:
                tool = get_tool_function(register_transition, "jira_transition_issue")
                result = asyncio.run(tool("KAN-15", status, comment=comment) if comment else tool("KAN-15", status))
                
                # Verify GET call
                mock_get.assert_called_once()
                assert "/transitions" in mock_get.call_args.args[0]
                
                # Verify POST call
                mock_post.assert_called_once()
                json_body = mock_post.call_args.kwargs["json_body"]
                assert "transition" in json_body
                
                if comment:
                    assert "update" in json_body and "comment" in json_body["update"]
    
    def test_handles_invalid_transition_error(self):
        """Tool returns error when transition is not available"""
        with patch('src.tools.jira_tools.jira_transition_issue.jira_api_get', new=AsyncMock(return_value={
            "transitions": [
                {"id": "11", "name": "Start", "to": {"name": "In Progress"}}
            ]
        })):
            tool = get_tool_function(register_transition, "jira_transition_issue")
            result = asyncio.run(tool("KAN-15", "NONEXISTENT_STATUS"))
            
            assert result["ok"] is False
            assert result["error"] == "no_matching_transition"
            assert "available_transitions" in result
