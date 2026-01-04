"""Tests for GitHub configuration loading and validation"""
import pytest
import os
from unittest.mock import patch
from src.config.github_config import GitHubConfig, get_github_config, extract_repo_info


class TestGitHubConfigSuccess:
    """Test successful GitHub configuration loading"""
    
    @patch.dict(os.environ, {
        'GIT_REPO_URL': 'https://github.com/owner/repo.git',
        'GITHUB_TOKEN': 'github_token_456',
        'GIT_DEFAULT_BRANCH': 'main'
    })
    def test_loads_config_from_env(self):
        config = get_github_config()
        assert isinstance(config, GitHubConfig)
        assert config.repo_url == 'https://github.com/owner/repo.git'
        assert config.token == 'github_token_456'
        assert config.default_branch == 'main'
    
    @patch.dict(os.environ, {
        'GIT_REPO_URL': 'https://github.com/owner/repo.git/',
        'GITHUB_TOKEN': 'github_token_456',
        'GIT_DEFAULT_BRANCH': 'main'
    })
    def test_removes_trailing_slash_from_url(self):
        config = get_github_config()
        assert config.repo_url == 'https://github.com/owner/repo.git'
    
    def test_config_is_immutable(self):
        config = GitHubConfig(
            repo_url='https://github.com/owner/repo.git',
            token='token',
            default_branch='main'
        )
        with pytest.raises(AttributeError):
            config.token = 'new_token'


class TestGitHubConfigMissingEnv:
    """Test GitHub configuration with missing environment variables"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_raises_error_when_repo_url_missing(self):
        with pytest.raises(RuntimeError) as exc:
            get_github_config()
        assert 'GIT_REPO_URL' in str(exc.value)
    
    @patch.dict(os.environ, {
        'GIT_REPO_URL': 'https://github.com/owner/repo.git',
        'GIT_DEFAULT_BRANCH': 'main'
    }, clear=True)
    def test_raises_error_when_token_missing(self):
        with pytest.raises(RuntimeError) as exc:
            get_github_config()
        assert 'GITHUB_TOKEN' in str(exc.value)
    
    @patch.dict(os.environ, {
        'GIT_REPO_URL': 'https://github.com/owner/repo.git',
        'GITHUB_TOKEN': 'github_token_456'
    }, clear=True)
    def test_raises_error_when_default_branch_missing(self):
        with pytest.raises(RuntimeError) as exc:
            get_github_config()
        assert 'GIT_DEFAULT_BRANCH' in str(exc.value)


class TestGitHubConfigInvalid:
    """Test GitHub configuration with invalid values"""
    
    @patch.dict(os.environ, {
        'GIT_REPO_URL': 'invalid-url',
        'GITHUB_TOKEN': 'github_token_456',
        'GIT_DEFAULT_BRANCH': 'main'
    }, clear=True)
    def test_raises_error_when_repo_url_invalid(self):
        with pytest.raises(RuntimeError):
            get_github_config()


class TestExtractRepoInfoHttpsWithGit:
    """Test extracting repo info from HTTPS URL with .git"""
    
    def test_extracts_owner_and_repo(self):
        owner, repo = extract_repo_info('https://github.com/owner/repo.git')
        assert owner == 'owner'
        assert repo == 'repo'


class TestExtractRepoInfoHttpsWithoutGit:
    """Test extracting repo info from HTTPS URL without .git"""
    
    def test_extracts_owner_and_repo(self):
        owner, repo = extract_repo_info('https://github.com/owner/repo')
        assert owner == 'owner'
        assert repo == 'repo'


class TestExtractRepoInfoWithTrailingSlash:
    """Test extracting repo info from URL with trailing slash"""
    
    def test_extracts_owner_and_repo(self):
        owner, repo = extract_repo_info('https://github.com/owner/repo.git/')
        assert owner == 'owner'
        assert repo == 'repo'


class TestExtractRepoInfoSshFormat:
    """Test extracting repo info from SSH format URL"""
    
    def test_extracts_repo_name(self):
        owner, repo = extract_repo_info('git@github.com:owner/repo.git')
        assert 'owner' in owner
        assert repo == 'repo'


class TestExtractRepoInfoInvalidFormat:
    """Test extracting repo info from invalid URL"""
    
    def test_raises_error_on_invalid_url(self):
        try:
            extract_repo_info('invalid-url')
            assert False, "Should have raised IndexError"
        except IndexError:
            pass
