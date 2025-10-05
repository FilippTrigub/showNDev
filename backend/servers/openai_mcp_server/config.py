import os
from typing import Dict

from dotenv import load_dotenv


class Config:
    """Configuration loader for OpenAI MCP server."""

    def __init__(self) -> None:
        load_dotenv()
        self.api_key = self._get_api_key()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        timeout_env = os.getenv("OPENAI_TIMEOUT", "120")
        try:
            self.timeout = float(timeout_env)
        except ValueError:
            raise ValueError(
                "OPENAI_TIMEOUT must be a numeric value representing seconds"
            )

    def _get_api_key(self) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Create an API key at https://platform.openai.com/ and set it "
                "before running the OpenAI MCP server."
            )
        return api_key

    @property
    def auth_header(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Authorization": f"Bearer {self.api_key}"}

        org_id = os.getenv("OPENAI_ORG_ID")
        if org_id:
            headers["OpenAI-Organization"] = org_id

        project_id = os.getenv("OPENAI_PROJECT_ID")
        if project_id:
            headers["OpenAI-Project"] = project_id

        return headers


config = Config()
