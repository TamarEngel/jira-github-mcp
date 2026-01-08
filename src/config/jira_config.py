import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  

@dataclass(frozen=True)
class JiraConfig:
    """Jira configuration with base URL, email, and API token."""
    base_url: str
    email: str
    api_token: str

def get_jira_config() -> JiraConfig:
    """
    Load and validate Jira configuration from environment variables.
    
    Returns:
        JiraConfig: Configuration object with base_url, email, and api_token
    
    Raises:
        RuntimeError: If required env vars are missing
    """
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not base_url or not email or not api_token:
        raise RuntimeError(
            "Missing Jira configuration. Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN in .env"
        )

    # Normalize base URL - WHY: Ensures consistent URL format for API calls
    base_url = base_url.rstrip("/")

    return JiraConfig(base_url=base_url, email=email, api_token=api_token)
