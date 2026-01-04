"""Tests for Jira configuration loading and validation"""
import pytest
import os
from unittest.mock import patch
from src.config.jira_config import JiraConfig, get_jira_config


class TestJiraConfigSuccess:
    """Test successful Jira configuration loading"""
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_EMAIL': 'user@example.com',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    })
    def test_loads_config_from_env(self):
        config = get_jira_config()
        assert isinstance(config, JiraConfig)
        assert config.base_url == 'https://your-instance.atlassian.net'
        assert config.email == 'user@example.com'
        assert config.api_token == 'jira_api_token_123'
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net/',
        'JIRA_EMAIL': 'user@example.com',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    })
    def test_removes_trailing_slash_from_url(self):
        config = get_jira_config()
        assert config.base_url == 'https://your-instance.atlassian.net'
    
    def test_config_is_immutable(self):
        config = JiraConfig(
            base_url='https://your-instance.atlassian.net',
            email='user@example.com',
            api_token='token'
        )
        with pytest.raises((AttributeError, RuntimeError)):
            config.email = 'new@example.com'


class TestJiraConfigMissingEnv:
    """Test Jira configuration with missing environment variables"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_raises_error_when_base_url_missing(self):
        with pytest.raises(RuntimeError) as exc:
            get_jira_config()
        assert 'JIRA_BASE_URL' in str(exc.value)
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    }, clear=True)
    def test_raises_error_when_email_missing(self):
        with pytest.raises(RuntimeError) as exc:
            get_jira_config()
        assert 'JIRA_EMAIL' in str(exc.value)
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_EMAIL': 'user@example.com'
    }, clear=True)
    def test_raises_error_when_api_token_missing(self):
        with pytest.raises(RuntimeError) as exc:
            get_jira_config()
        assert 'JIRA_API_TOKEN' in str(exc.value)


class TestJiraConfigEmpty:
    """Test Jira configuration with empty values"""
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': '',
        'JIRA_EMAIL': 'user@example.com',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    }, clear=True)
    def test_raises_error_when_base_url_empty(self):
        with pytest.raises(RuntimeError) as exc:
            get_jira_config()
        assert 'Missing Jira configuration' in str(exc.value)
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_EMAIL': '',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    }, clear=True)
    def test_raises_error_when_email_empty(self):
        with pytest.raises(RuntimeError) as exc:
            get_jira_config()
        assert 'Missing Jira configuration' in str(exc.value)
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_EMAIL': 'user@example.com',
        'JIRA_API_TOKEN': ''
    }, clear=True)
    def test_raises_error_when_api_token_empty(self):
        with pytest.raises(RuntimeError) as exc:
            get_jira_config()
        assert 'Missing Jira configuration' in str(exc.value)


class TestJiraConfigDataclass:
    """Test Jira configuration dataclass properties"""
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_EMAIL': 'user@example.com',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    })
    def test_config_equality(self):
        config1 = get_jira_config()
        config2 = get_jira_config()
        assert config1 == config2
    
    @patch.dict(os.environ, {
        'JIRA_BASE_URL': 'https://your-instance.atlassian.net',
        'JIRA_EMAIL': 'user@example.com',
        'JIRA_API_TOKEN': 'jira_api_token_123'
    })
    def test_config_has_all_required_fields(self):
        config = get_jira_config()
        assert hasattr(config, 'base_url')
        assert hasattr(config, 'email')
        assert hasattr(config, 'api_token')
