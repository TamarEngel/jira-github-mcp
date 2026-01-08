"""Tests for GitHub API integration"""
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from src.providers.github.github_api import github_api_get, github_api_post, github_api_put


class TestGitHubApiGetSuccess:
    """Test successful GitHub API GET request"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_returns_response_data(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='test_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "name": "owner/repo"}
        mock_client.request.return_value = mock_response
        
        result = await github_api_get('/repos/owner/repo')
        
        assert result['id'] == 123
        assert result['name'] == 'owner/repo'


class TestGitHubApiGetWithParams:
    """Test GitHub API GET request passes parameters"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_passes_params(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='test_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"pull_requests": []}
        mock_client.request.return_value = mock_response
        
        params = {"state": "open", "sort": "updated"}
        await github_api_get('/repos/owner/repo/pulls', params=params)
        
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs['params'] == params


class TestGitHubApiGetErrors:
    """Test GitHub API GET request error handling"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_raises_error_on_401(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='invalid_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Bad credentials'
        mock_client.request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            await github_api_get('/user')
        
        assert '401' in str(exc.value)
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_raises_error_on_404(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='github_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_client.request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            await github_api_get('/repos/nonexistent/repo')
        
        assert '404' in str(exc.value)


class TestGitHubApiPostSuccess:
    """Test successful GitHub API POST request"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_returns_response_data(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='test_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 456, "number": 5}
        mock_client.request.return_value = mock_response
        
        body = {"title": "New PR"}
        result = await github_api_post('/repos/owner/repo/pulls', json_body=body)
        
        assert result['number'] == 5
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_passes_params(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='test_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_client.request.return_value = mock_response
        
        body = {"name": "new-branch"}
        params = {"auto_init": True}
        await github_api_post('/repos/owner/repo/git/refs', json_body=body, params=params)
        
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs['params'] == params


class TestGitHubApiPostErrors:
    """Test GitHub API POST request error handling"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_raises_error_on_422(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='github_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = 'No commits between main and feature-branch'
        mock_client.request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            await github_api_post('/repos/owner/repo/pulls', json_body={})
        
        assert '422' in str(exc.value)


class TestGitHubApiPutSuccess:
    """Test successful GitHub API PUT request"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_returns_merge_response(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='test_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sha": "abc123", "message": "Pull Request merged"}
        mock_client.request.return_value = mock_response
        
        body = {"merge_method": "squash"}
        result = await github_api_put('/repos/owner/repo/pulls/1/merge', json_body=body)
        
        assert result['sha'] == 'abc123'
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_passes_params(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='test_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_client.request.return_value = mock_response
        
        body = {"merge_method": "rebase"}
        params = {"commit_title": "custom title"}
        await github_api_put('/repos/owner/repo/pulls/1/merge', json_body=body, params=params)
        
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs['params'] == params


class TestGitHubApiPutErrors:
    """Test GitHub API PUT request error handling"""
    
    @pytest.mark.asyncio
    @patch('src.providers.github.github_api.get_github_config')
    @patch('src.providers.github.github_api.httpx.AsyncClient')
    async def test_raises_error_on_404(self, mock_client_class, mock_config):
        mock_config.return_value = MagicMock(token='github_token')
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'PR not found'
        mock_client.request.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            await github_api_put('/repos/owner/repo/pulls/999/merge', json_body={})
        
        assert '404' in str(exc.value)
