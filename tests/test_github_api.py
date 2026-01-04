"""Tests for GitHub API integration"""
import pytest
from unittest.mock import patch, MagicMock
import requests
from src.providers.github.github_api import github_api_get, github_api_post, github_api_put


class TestGitHubApiGetSuccess:
    """Test successful GitHub API GET request"""
    
    @patch('src.providers.github.github_api._github_request')
    def test_returns_response_data(self, mock_request):
        mock_request.return_value = {"id": 123, "name": "owner/repo"}
        
        result = github_api_get('/repos/owner/repo')
        
        assert result['id'] == 123
        assert result['name'] == 'owner/repo'
        mock_request.assert_called_once_with('GET', '/repos/owner/repo', params=None)


class TestGitHubApiGetWithParams:
    """Test GitHub API GET request passes parameters"""
    
    @patch('src.providers.github.github_api._github_request')
    def test_passes_params(self, mock_request):
        mock_request.return_value = {"pull_requests": []}
        
        params = {"state": "open", "sort": "updated"}
        github_api_get('/repos/owner/repo/pulls', params=params)
        
        mock_request.assert_called_once_with('GET', '/repos/owner/repo/pulls', params=params)


class TestGitHubApiGetErrors:
    """Test GitHub API GET request error handling"""
    
    @patch('src.providers.github.github_api.requests.request')
    @patch('src.providers.github.github_api.get_github_config')
    def test_raises_error_on_401(self, mock_config, mock_request):
        mock_config.return_value.token = 'invalid_token'
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = 'Bad credentials'
        mock_request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            github_api_get('/user')
        
        assert '401' in str(exc.value)
    
    @patch('src.providers.github.github_api.requests.request')
    @patch('src.providers.github.github_api.get_github_config')
    def test_raises_error_on_404(self, mock_config, mock_request):
        mock_config.return_value.token = 'github_token'
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            github_api_get('/repos/nonexistent/repo')
        
        assert '404' in str(exc.value)


class TestGitHubApiPostSuccess:
    """Test successful GitHub API POST request"""
    
    @patch('src.providers.github.github_api._github_request')
    def test_returns_response_data(self, mock_request):
        mock_request.return_value = {"id": 456, "number": 5}
        
        body = {"title": "New PR"}
        result = github_api_post('/repos/owner/repo/pulls', json_body=body)
        
        assert result['number'] == 5
        mock_request.assert_called_once_with('POST', '/repos/owner/repo/pulls', json_body=body, params=None)
    
    @patch('src.providers.github.github_api._github_request')
    def test_passes_params(self, mock_request):
        mock_request.return_value = {"ok": True}
        
        body = {"name": "new-branch"}
        params = {"auto_init": True}
        github_api_post('/repos/owner/repo/git/refs', json_body=body, params=params)
        
        mock_request.assert_called_once_with(
            'POST', '/repos/owner/repo/git/refs',
            json_body=body, params=params
        )


class TestGitHubApiPostErrors:
    """Test GitHub API POST request error handling"""
    
    @patch('src.providers.github.github_api.requests.request')
    @patch('src.providers.github.github_api.get_github_config')
    def test_raises_error_on_422(self, mock_config, mock_request):
        mock_config.return_value.token = 'github_token'
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 422
        mock_response.text = 'No commits between main and feature-branch'
        mock_request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            github_api_post('/repos/owner/repo/pulls', json_body={})
        
        assert '422' in str(exc.value)


class TestGitHubApiPutSuccess:
    """Test successful GitHub API PUT request"""
    
    @patch('src.providers.github.github_api._github_request')
    def test_returns_merge_response(self, mock_request):
        mock_request.return_value = {"sha": "abc123", "message": "Pull Request merged"}
        
        body = {"merge_method": "squash"}
        result = github_api_put('/repos/owner/repo/pulls/1/merge', json_body=body)
        
        assert result['sha'] == 'abc123'
        mock_request.assert_called_once_with('PUT', '/repos/owner/repo/pulls/1/merge', json_body=body, params=None)
    
    @patch('src.providers.github.github_api._github_request')
    def test_passes_params(self, mock_request):
        mock_request.return_value = {"ok": True}
        
        body = {"merge_method": "rebase"}
        params = {"commit_title": "custom title"}
        github_api_put('/repos/owner/repo/pulls/1/merge', json_body=body, params=params)
        
        mock_request.assert_called_once_with(
            'PUT', '/repos/owner/repo/pulls/1/merge',
            json_body=body, params=params
        )


class TestGitHubApiPutErrors:
    """Test GitHub API PUT request error handling"""
    
    @patch('src.providers.github.github_api.requests.request')
    @patch('src.providers.github.github_api.get_github_config')
    def test_raises_error_on_404(self, mock_config, mock_request):
        mock_config.return_value.token = 'github_token'
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = 'PR not found'
        mock_request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            github_api_put('/repos/owner/repo/pulls/999/merge', json_body={})
        
        assert '404' in str(exc.value)
