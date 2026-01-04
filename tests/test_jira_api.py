"""Tests for Jira API integration"""
import pytest
from unittest.mock import patch, MagicMock
import requests
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
    
    @patch('src.providers.jira.jira_api.requests.get')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_returns_issue_data(self, mock_config, mock_get):
        mock_config.return_value = create_config_mocks()
        mock_get.return_value = create_response_mock(json_value={"key": "KAN-1", "summary": "Bug"})
        
        result = jira_api_get('/issue/KAN-1')
        
        assert result['key'] == 'KAN-1'
        assert result['summary'] == 'Bug'


class TestJiraApiGetWithParams:
    """Test Jira API GET request with parameters"""
    
    @patch('src.providers.jira.jira_api.requests.get')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_passes_params_to_request(self, mock_config, mock_get):
        mock_config.return_value = create_config_mocks()
        mock_get.return_value = create_response_mock(json_value={"issues": []})
        
        params = {"fields": "summary,status"}
        jira_api_get('/search', params=params)
        
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs['params'] == params


@pytest.mark.parametrize("status_code,text", [(404, "Not found"), (401, "Unauthorized")])
class TestJiraApiGetErrors:
    """Test Jira API GET request error handling"""
    
    @patch('src.providers.jira.jira_api.requests.get')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_raises_error_on_http_error(self, mock_config, mock_get, status_code, text):
        mock_config.return_value = create_config_mocks()
        mock_get.return_value = create_response_mock(ok=False, status_code=status_code, text=text)
        
        with pytest.raises(RuntimeError) as exc:
            jira_api_get('/issue/INVALID-999')
        
        assert str(status_code) in str(exc.value)


@pytest.mark.parametrize("exc_class", [requests.Timeout, requests.ConnectionError])
class TestJiraApiGetNetworkErrors:
    """Test Jira API GET request network error handling"""
    
    @patch('src.providers.jira.jira_api.requests.get')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_propagates_network_error(self, mock_config, mock_get, exc_class):
        mock_config.return_value = create_config_mocks()
        mock_get.side_effect = exc_class('Network error')
        
        with pytest.raises(exc_class):
            jira_api_get('/issue/KAN-1')


class TestJiraApiGetAuthentication:
    """Test Jira API GET request uses authentication"""
    
    @patch('src.providers.jira.jira_api.requests.get')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_includes_auth_header(self, mock_config, mock_get):
        mock_config.return_value = create_config_mocks()
        mock_get.return_value = create_response_mock(json_value={"key": "KAN-1"})
        
        jira_api_get('/issue/KAN-1')
        
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs['auth'] is not None


class TestJiraApiPostSuccess:
    """Test successful Jira API POST request"""
    
    @patch('src.providers.jira.jira_api.requests.post')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_returns_response_data(self, mock_config, mock_post):
        mock_config.return_value = create_config_mocks()
        mock_post.return_value = create_response_mock(
            status_code=200,
            text='{"id":"123","success":true}',
            json_value={"id": "123", "success": True}
        )
        
        result = jira_api_post('/issue/KAN-1/transitions', json_body={"transition": {"id": "10"}})
        
        assert result["id"] == "123"
        assert result["success"] is True


class TestJiraApiPostNoContent:
    """Test Jira API POST request with 204 No Content response"""
    
    @patch('src.providers.jira.jira_api.requests.post')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_handles_204_response(self, mock_config, mock_post):
        mock_config.return_value = create_config_mocks()
        mock_post.return_value = create_response_mock(status_code=204)
        
        result = jira_api_post('/issue/KAN-1/transitions', json_body={"transition": {"id": "10"}})
        
        assert result['ok'] is True
        assert result['status_code'] == 204


class TestJiraApiPostJsonAndHeaders:
    """Test Jira API POST request passes JSON body and headers correctly"""
    
    @patch('src.providers.jira.jira_api.requests.post')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_sends_json_body_and_headers(self, mock_config, mock_post):
        mock_config.return_value = create_config_mocks()
        mock_post.return_value = create_response_mock(
            text='{"success":true}',
            json_value={"success": True}
        )
        
        body = {"transition": {"id": "10"}}
        result = jira_api_post('/issue/KAN-1/transitions', json_body=body)
        
        # Verify JSON body and headers were sent correctly
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs['json'] == body
        headers = call_kwargs['headers']
        assert headers['Content-Type'] == 'application/json'
        assert headers['Accept'] == 'application/json'
        
        # Verify response is parsed correctly
        assert result["success"] is True


class TestJiraApiPostErrors:
    """Test Jira API POST request error handling"""
    
    @patch('src.providers.jira.jira_api.requests.post')
    @patch('src.providers.jira.jira_api.get_jira_config')
    def test_raises_error_on_400(self, mock_config, mock_post):
        mock_config.return_value = create_config_mocks()
        mock_post.return_value = create_response_mock(ok=False, status_code=400, text='Invalid transition')
        
        with pytest.raises(RuntimeError) as exc:
            jira_api_post('/issue/KAN-1/transitions', json_body={})
        
        assert '400' in str(exc.value)
