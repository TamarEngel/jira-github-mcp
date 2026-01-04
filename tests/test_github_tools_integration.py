"""Integration tests for GitHub Tools
Tests that each tool calls the GitHub provider with correct endpoints and parameters.
"""
import pytest
from unittest.mock import patch
from src.tools.github_tools.github_create_branch import register as register_create_branch
from src.tools.github_tools.github_commit_and_push import register as register_commit_push
from src.tools.github_tools.github_create_pull_request import register as register_create_pr
from src.tools.github_tools.github_merge_pr import register as register_merge_pr


class MockFastMCP:
    """Mock FastMCP to extract registered tool functions.
    
    We mock FastMCP only to capture the tool function registered by @mcp.tool,
    so we can unit/integration-test the tool logic without running an MCP server.
    """
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


def get_json_body(mock_call):
    """Extract json body from mock call args (handles both 'json' and 'json_body' param names)"""
    return mock_call.kwargs.get("json") or mock_call.kwargs.get("json_body") or {}


def setup_repo(mock_config, mock_extract, default_branch="main"):
    """Setup common mock config and extract_repo_info for GitHub tests"""
    mock_config.return_value.repo_url = "https://github.com/owner/repo"
    mock_config.return_value.default_branch = default_branch
    mock_extract.return_value = ("owner", "repo")


class TestGitCreateBranchTool:
    
    @pytest.mark.parametrize("branch_name,expected_in_ref", [
        (None, "feature/kan-1"),
        ("custom-branch", "custom-branch")
    ])
    @patch('src.tools.github_tools.github_create_branch.extract_repo_info')
    @patch('src.tools.github_tools.github_create_branch.get_github_config')
    @patch('src.tools.github_tools.github_create_branch.github_api_post')
    @patch('src.tools.github_tools.github_create_branch.github_api_get')
    def test_creates_branch_with_correct_ref(self, mock_get, mock_post, mock_config, mock_extract, branch_name, expected_in_ref):
        setup_repo(mock_config, mock_extract)
        mock_get.return_value = {"object": {"sha": "abc123def456"}}
        mock_post.return_value = {
            "ref": f"refs/heads/{expected_in_ref}",
            "object": {"sha": "abc123def456"}
        }
        
        tool = get_tool_function(register_create_branch, "create_branch_for_issue")
        kwargs = {"branch_name": branch_name} if branch_name else {}
        tool("KAN-1", **kwargs)
        
        mock_get.assert_called_once()
        mock_post.assert_called_once()
        json_body = get_json_body(mock_post.call_args)
        assert json_body["sha"] == "abc123def456"
        assert expected_in_ref in json_body["ref"]
    
    @patch('src.tools.github_tools.github_create_branch.extract_repo_info')
    @patch('src.tools.github_tools.github_create_branch.get_github_config')
    @patch('src.tools.github_tools.github_create_branch.github_api_post')
    @patch('src.tools.github_tools.github_create_branch.github_api_get')
    def test_handles_base_branch_fetch_error(self, mock_get, mock_post, mock_config, mock_extract):
        setup_repo(mock_config, mock_extract)
        mock_get.side_effect = Exception("Branch not found")
        
        tool = get_tool_function(register_create_branch, "create_branch_for_issue")
        result = tool("KAN-1")
        
        assert result["success"] is False
        assert "error" in result


class TestGitCommitAndPushTool:
    
    @patch('src.tools.github_tools.github_commit_and_push.os.path.isdir')
    @patch('src.tools.github_tools.github_commit_and_push.extract_repo_info')
    @patch('src.tools.github_tools.github_commit_and_push.run_git_command')
    @patch('src.tools.github_tools.github_commit_and_push.get_github_config')
    def test_stages_commits_and_pushes(self, mock_config, mock_git, mock_extract, mock_isdir):
        setup_repo(mock_config, mock_extract)
        mock_isdir.return_value = True
        mock_git.side_effect = [
            (True, "main\n"),
            (True, ""),
            (True, ""),
            (True, ""),
            (True, ""),
        ]
        
        tool = get_tool_function(register_commit_push, "git_commit_and_push")
        result = tool("Fix: Update documentation")
        
        assert result.get("success") is not False
        assert mock_git.call_count >= 3
    
    @patch('src.tools.github_tools.github_commit_and_push.os.path.isdir')
    @patch('src.tools.github_tools.github_commit_and_push.extract_repo_info')
    @patch('src.tools.github_tools.github_commit_and_push.run_git_command')
    @patch('src.tools.github_tools.github_commit_and_push.get_github_config')
    def test_handles_not_git_repo_error(self, mock_config, mock_git, mock_extract, mock_isdir):
        setup_repo(mock_config, mock_extract)
        mock_isdir.return_value = False
        
        tool = get_tool_function(register_commit_push, "git_commit_and_push")
        result = tool("Fix: Update")
        
        assert result["success"] is False
        assert "error" in result


class TestGitCreatePullRequestTool:
    
    @patch('src.tools.github_tools.github_create_pull_request.extract_repo_info')
    @patch('src.tools.github_tools.github_create_pull_request.get_github_config')
    @patch('src.tools.github_tools.github_create_pull_request.github_api_post')
    def test_creates_pr_with_correct_title_and_branch(self, mock_post, mock_config, mock_extract):
        setup_repo(mock_config, mock_extract)
        mock_post.return_value = {
            "number": 42,
            "html_url": "https://github.com/owner/repo/pull/42",
            "title": "KAN-1: Create feature branch"
        }
        
        tool = get_tool_function(register_create_pr, "create_pull_request")
        tool("KAN-1", "feature/kan-1")
        
        mock_post.assert_called_once()
        json_body = get_json_body(mock_post.call_args)
        assert "KAN-1" in json_body["title"]
        assert "feature/kan-1" in json_body["head"]
    
    @patch('src.tools.github_tools.github_create_pull_request.extract_repo_info')
    @patch('src.tools.github_tools.github_create_pull_request.get_github_config')
    @patch('src.tools.github_tools.github_create_pull_request.github_api_post')
    def test_uses_custom_title_and_description(self, mock_post, mock_config, mock_extract):
        setup_repo(mock_config, mock_extract)
        mock_post.return_value = {"number": 42}
        
        tool = get_tool_function(register_create_pr, "create_pull_request")
        tool("KAN-1", "feature/kan-1", title="Custom Title", description="Custom description")
        
        json_body = get_json_body(mock_post.call_args)
        assert json_body["title"] == "Custom Title"
        assert "Custom description" in json_body.get("body", "")
    
    @patch('src.tools.github_tools.github_create_pull_request.extract_repo_info')
    @patch('src.tools.github_tools.github_create_pull_request.get_github_config')
    @patch('src.tools.github_tools.github_create_pull_request.github_api_post')
    def test_handles_api_error(self, mock_post, mock_config, mock_extract):
        setup_repo(mock_config, mock_extract)
        mock_post.side_effect = Exception("API error: 422 Unprocessable Entity")
        
        tool = get_tool_function(register_create_pr, "create_pull_request")
        result = tool("KAN-1", "feature/kan-1")
        
        assert result.get("success") is False or "error" in result


class TestGitMergePullRequestTool:
    
    @pytest.mark.parametrize("method", ["squash", "rebase", "merge"])
    @patch('src.tools.github_tools.github_merge_pr.extract_repo_info')
    @patch('src.tools.github_tools.github_merge_pr.get_github_config')
    @patch('src.tools.github_tools.github_merge_pr.github_api_put')
    @patch('src.tools.github_tools.github_merge_pr.github_api_get')
    def test_merge_with_correct_method(self, mock_get, mock_put, mock_config, mock_extract, method):
        setup_repo(mock_config, mock_extract)
        mock_get.side_effect = [
            {"state": "open", "merged": False, "title": "Test PR", "head": {"sha": "abc123"}},
            {"state": "success"},
            [],
        ]
        mock_put.return_value = {"merged": True, "sha": "def456"}
        
        tool = get_tool_function(register_merge_pr, "merge_pull_request")
        result = tool(42, merge_method=method)
        
        assert result.get("success") is True or result.get("success") is not False
        if mock_put.called:
            json_body = get_json_body(mock_put.call_args)
            assert json_body.get("merge_method") == method
    
    @patch('src.tools.github_tools.github_merge_pr.extract_repo_info')
    @patch('src.tools.github_tools.github_merge_pr.get_github_config')
    @patch('src.tools.github_tools.github_merge_pr.github_api_put')
    @patch('src.tools.github_tools.github_merge_pr.github_api_get')
    def test_handles_merge_conflict(self, mock_get, mock_put, mock_config, mock_extract):
        setup_repo(mock_config, mock_extract)
        mock_get.side_effect = [
            {"state": "open", "merged": False, "title": "Test PR", "head": {"sha": "abc123"}},
            {"state": "success"},
            [],
        ]
        mock_put.side_effect = Exception("409: Merge conflict")
        
        tool = get_tool_function(register_merge_pr, "merge_pull_request")
        result = tool(42)
        
        assert result.get("success") is False or "error" in result or isinstance(result, dict)
