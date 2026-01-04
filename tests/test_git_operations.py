"""Tests for Git operations"""
import pytest
from unittest.mock import patch, MagicMock
from src.providers.github.git_operations import run_git_command


class TestRunGitCommandSuccess:
    """Test successful git command execution"""
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_returns_success_and_output(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="commit abc123",
            stderr=""
        )
        
        success, output = run_git_command(['git', 'log', '--oneline', '-1'])
        
        assert success is True
        assert output == "commit abc123"
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_runs_command_with_args(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        
        run_git_command(['git', 'commit', '-m', 'test message'])
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'commit', '-m', 'test message']


class TestRunGitCommandFailure:
    """Test git command execution failures"""
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_returns_failure_on_non_zero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
            stderr="fatal: not a git repository"
        )
        
        success, output = run_git_command(['git', 'status'])
        
        assert success is False
        assert "fatal: not a git repository" in output
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_returns_failure_with_merge_conflict(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="CONFLICT (content): Merge conflict in file.txt"
        )
        
        success, output = run_git_command(['git', 'merge', 'feature-branch'])
        
        assert success is False
        assert "CONFLICT" in output


class TestRunGitCommandWithCwd:
    """Test git command execution with custom working directory"""
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_passes_cwd_parameter(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        
        run_git_command(['git', 'status'], cwd='/path/to/repo')
        
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get('cwd') == '/path/to/repo'
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_executes_in_default_dir_when_cwd_not_provided(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        
        run_git_command(['git', 'log'])
        
        call_kwargs = mock_run.call_args[1]
        assert 'cwd' not in call_kwargs or call_kwargs.get('cwd') is None


class TestRunGitCommandEdgeCases:
    """Test edge cases for git command execution"""
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_handles_multiline_output(self, mock_run):
        multiline_output = "line1\nline2\nline3"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=multiline_output,
            stderr=""
        )
        
        success, result = run_git_command(['git', 'log'])
        
        assert success is True
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_handles_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr=""
        )
        
        success, result = run_git_command(['git', 'diff'])
        
        assert success is True
        assert result == ""
    
    @patch('src.providers.github.git_operations.subprocess.run')
    def test_handles_unicode_in_output(self, mock_run):
        unicode_output = "commit: fr-FR, en-US, status: complete"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=unicode_output,
            stderr=""
        )
        
        success, result = run_git_command(['git', 'log'])
        
        assert success is True
        assert "fr-FR" in result
        assert "en-US" in result
        assert "complete" in result