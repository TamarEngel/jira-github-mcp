"""Tests for Jira API integration"""
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from src.providers.jira.jira_api import jira_api_get, jira_api_post


def create_config_mocks():
    """Factory to create config mocks"""
    config = MagicMock()
    config.base_url = 'https://jira.example.com'
    config.email = 'user@example.com'
    config.api_token = 'secret'
    return config


def create_response_mock(ok=True, status_code=200, json_value=None, text=''):
    """Factory to create response mocks"""
    response = MagicMock()
    response.ok = ok
    response.status_code = status_code
    response.text = text
    response.json.return_value = json_value or {}
    return response


class TestJiraApiGetSuccess:
    """Test successful Jira API GET request"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_returns_issue_data(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        # Mock the async context manager and client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "KAN-1", "summary": "Bug"}'
        mock_response.json.return_value = {"key": "KAN-1", "summary": "Bug"}
        mock_client.get.return_value = mock_response
        
        result = await jira_api_get('/issue/KAN-1')
        
        assert result['key'] == 'KAN-1'
        assert result['summary'] == 'Bug'


class TestJiraApiGetWithParams:
    """Test Jira API GET request with parameters"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_passes_params_to_request(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"issues": []}'
        mock_response.json.return_value = {"issues": []}
        mock_client.get.return_value = mock_response
        
        params = {"fields": "summary,status"}
        await jira_api_get('/search', params=params)
        
        call_kwargs = mock_client.get.call_args.kwargs
        assert call_kwargs['params'] == params


@pytest.mark.parametrize("status_code,text", [(404, "Not found"), (401, "Unauthorized")])
class TestJiraApiGetErrors:
    """Test Jira API GET request error handling"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_raises_error_on_http_error(self, mock_client_class, mock_config, status_code, text):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.text = text
        mock_client.get.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            await jira_api_get('/issue/INVALID-999')
        
        assert str(status_code) in str(exc.value)


@pytest.mark.parametrize("exc_class", [httpx.TimeoutException, httpx.ConnectError])
class TestJiraApiGetNetworkErrors:
    """Test Jira API GET request network error handling"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_propagates_network_error(self, mock_client_class, mock_config, exc_class):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = exc_class('Network error')
        
        with pytest.raises(exc_class):
            await jira_api_get('/issue/KAN-1')


class TestJiraApiGetAuthentication:
    """Test Jira API GET request uses authentication"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_includes_auth_header(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "KAN-1"}'
        mock_response.json.return_value = {"key": "KAN-1"}
        mock_client.get.return_value = mock_response
        
        await jira_api_get('/issue/KAN-1')
        
        call_kwargs = mock_client.get.call_args.kwargs
        assert call_kwargs['auth'] is not None


class TestJiraApiPostSuccess:
    """Test successful Jira API POST request"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_returns_response_data(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"id":"123","success":true}'
        mock_response.json.return_value = {"id": "123", "success": True}
        mock_client.post.return_value = mock_response
        
        result = await jira_api_post('/issue/KAN-1/transitions', json_body={"transition": {"id": "10"}})
        
        assert result["id"] == "123"
        assert result["success"] is True


class TestJiraApiPostNoContent:
    """Test Jira API POST request with 204 No Content response"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_handles_204_response(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ''
        mock_client.post.return_value = mock_response
        
        result = await jira_api_post('/issue/KAN-1/transitions', json_body={"transition": {"id": "10"}})
        
        assert result['ok'] is True
        assert result['status_code'] == 204


class TestJiraApiPostJsonAndHeaders:
    """Test Jira API POST request passes JSON body and headers correctly"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_sends_json_body_and_headers(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"success":true}'
        mock_response.json.return_value = {"success": True}
        mock_client.post.return_value = mock_response
        
        body = {"transition": {"id": "10"}}
        result = await jira_api_post('/issue/KAN-1/transitions', json_body=body)
        
        # Verify JSON body and headers were sent correctly
        call_kwargs = mock_client.post.call_args.kwargs
        assert call_kwargs['json'] == body
        headers = call_kwargs['headers']
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/json'
        
        # Verify response is parsed correctly
        assert result["success"] is True


class TestJiraApiPostErrors:
    """Test Jira API POST request error handling"""
    
    @pytest.mark.asyncio
    @patch('src.providers.jira.jira_api.get_jira_config')
    @patch('src.providers.jira.jira_api.httpx.AsyncClient')
    async def test_raises_error_on_400(self, mock_client_class, mock_config):
        mock_config.return_value = create_config_mocks()
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Invalid transition'
        mock_client.post.return_value = mock_response
        
        with pytest.raises(RuntimeError) as exc:
            await jira_api_post('/issue/KAN-1/transitions', json_body={})
        
        assert '400' in str(exc.value)
