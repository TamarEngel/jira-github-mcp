import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class GitHubConfig:
    """GitHub configuration with repo URL, token, and default branch."""
    repo_url: str
    token: str
    default_branch: str


def get_github_config() -> GitHubConfig:
    """
    Load and validate GitHub configuration from environment variables.
    
    Returns:
        GitHubConfig: Configuration object
    
    Raises:
        RuntimeError: If required env vars are missing or URL format is invalid
    """
    repo_url = os.getenv("GIT_REPO_URL")
    token = os.getenv("GITHUB_TOKEN")
    default_branch = os.getenv("GIT_DEFAULT_BRANCH")

    if not repo_url or not token or not default_branch:
        raise RuntimeError(
            "Missing GitHub configuration. "
            "Please set GIT_REPO_URL, GITHUB_TOKEN, and GIT_DEFAULT_BRANCH in .env"
        )
    
    # Validate repository URL format - WHY: Ensures URL can be parsed correctly later
    try:
        parts = repo_url.rstrip("/").replace(".git", "").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid repository URL format")
    except Exception as e:
        raise RuntimeError(f"Invalid GIT_REPO_URL format: {repo_url}") from e

    return GitHubConfig(
        repo_url=repo_url.rstrip("/"),
        token=token,
        default_branch=default_branch
    )


def extract_repo_info(repo_url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    parts = repo_url.rstrip("/").replace(".git", "").split("/")
    return parts[-2], parts[-1]
