"""
MCP Agent Executor Module

This module provides parallel execution of AI models/MCP servers using mcp-agent
with proper concurrent processing and result standardization.
"""
import os
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / '.env')

# Import mcp-agent components (following llm_agent.py pattern)
from mcp_agent.app import MCPApp
from mcp_agent.config import (
    Settings,
    LoggerSettings,
    MCPSettings,
    MCPServerSettings,
    OpenAISettings,
)
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM


@dataclass
class ExecutorResult:
    """Result object for parallel executor operations"""
    prompt_name: str
    server_name: str
    content: Optional[str] = None
    error: Optional[str] = None
    status: str = "generated"
    execution_time: Optional[float] = None

    def __repr__(self):
        return f"ExecutorResult(prompt='{self.prompt_name}', server='{self.server_name}', status='{self.status}')"


class MCPAgentExecutor:
    """
    MCP Agent Executor using mcp-agent library for LLM-powered execution
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "gpt-5",
                 base_url: Optional[str] = None,
                 provider: Optional[str] = None,
                 default_headers: Optional[Dict[str, str]] = None):
        """
        Initialize the MCP Agent executor
        
        Args:
            api_key: Optional API key override for the selected provider
            model: Default model name for the selected provider
            base_url: API base URL for the selected provider
            provider: LLM provider identifier (blackbox, openai, openrouter)
            default_headers: Optional extra HTTP headers for OpenAI-compatible clients
        """
        load_dotenv(override=True)
        self.provider = (provider or os.getenv("MCP_LLM_PROVIDER") or "openai").strip().lower()
        self._provider_config = self._resolve_provider_config(
            api_key=api_key,
            model=model,
            base_url=base_url,
            default_headers=default_headers,
        )

        self.api_key = self._provider_config["api_key"]
        self.model = self._provider_config["model"]
        self.base_url = self._provider_config["base_url"]
        self.default_headers = self._provider_config.get("default_headers")
        self.app = None

        # Available MCP servers configuration
        self._server_config = {
            "blackbox": {
                "command": "uv",
                "args": ["run", "python", "servers/bbai_mcp_server/blackbox_mcp_server/server.py"],
                "cwd": str(Path(__file__).parent),
                "env": {"BLACKBOX_API_KEY": os.getenv("BLACKBOX_API_KEY")}
            },
            "openai": {
                "command": "uv",
                "args": ["run", "python", "servers/openai_mcp_server/server.py"],
                "cwd": str(Path(__file__).parent),
                "env": {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
            },
            "bluesky": {
                "command": "uv",
                "args": ["run", "python", "servers/bluesky-mcp-python/server.py"],
                "cwd": str(Path(__file__).parent),
                "env": {"BLUESKY_IDENTIFIER": os.getenv('BLUESKY_IDENTIFIER'),
                        "BLUESKY_APP_PASSWORD": os.getenv('BLUESKY_APP_PASSWORD'),
                        "BLUESKY_SERVICE_URL": os.getenv('BLUESKY_SERVICE_URL')}
            },
            "linkedin": {
                "command": "uv",
                "args": ["run", "python", "servers/linkedin-mcp/linkedin_mcp/server.py"],
                "cwd": str(Path(__file__).parent),
                "env": {"LINKEDIN_CLIENT_ID": os.getenv("LINKEDIN_CLIENT_ID"),
                        "LINKEDIN_CLIENT_SECRET": os.getenv("LINKEDIN_CLIENT_SECRET"),
                        "LINKEDIN_REDIRECT_URI": os.getenv("LINKEDIN_REDIRECT_URI")}
            },
            "twitter": {
                "command": "node",
                "args": ["servers/twitter-mcp/build/index.js"],
                "cwd": str(Path(__file__).parent),
                "env": {"API_KEY": os.getenv("API_KEY"),
                        "API_SECRET_KEY": os.getenv("API_SECRET_KEY"),
                        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),
                        "ACCESS_TOKEN_SECRET": os.getenv("ACCESS_TOKEN_SECRET")}
            },
            "mongodb": {
                "command": "npx",
                "args": ["-y", "mongodb-mcp-server", "--connectionString",
                         os.getenv("MONGODB_URI"), ],
                "cwd": str(Path(__file__).parent),
                "env": {
                    "MONGODB_URI": os.getenv("MONGODB_URI"),
                    "MONGODB_DB_NAME": os.getenv("MONGODB_DB_NAME")}
            }
        }
        self._setup_mcp_app()

    def update_server_env(self, env_updates: Dict[str, Optional[str]],
                          server_names: Optional[List[str]] = None) -> None:
        """Refresh MCP server environment variables after runtime updates."""
        target_servers = server_names or list(self._server_config.keys())

        for server_name in target_servers:
            if server_name not in self._server_config:
                continue

            server_env = self._server_config[server_name].get("env", {})
            for key, value in env_updates.items():
                if value is None:
                    server_env.pop(key, None)
                else:
                    server_env[key] = value

        # Rebuild MCP app so new env vars propagate to subprocess configs
        self._setup_mcp_app()

    def _setup_mcp_app(self):
        """Setup MCP application with server configurations using Settings"""
        # Build server configurations based on requested servers
        load_dotenv(override=True)
        mcp_servers = {}
        for server_name, config in self._server_config.items():
            mcp_servers[server_name] = MCPServerSettings(
                command=config["command"],
                args=config["args"],
                cwd=config["cwd"],
                env=config["env"]
            )

        # Create settings with MCP server configurations
        openai_settings_kwargs = dict(
            api_key=self.api_key,
            base_url=self.base_url,
            default_model=self.model,
        )
        if self.default_headers:
            openai_settings_kwargs["default_headers"] = self.default_headers

        settings = Settings(
            execution_engine="asyncio",
            logger=LoggerSettings(type="console", level="info"),
            mcp=MCPSettings(servers=mcp_servers),
            openai=OpenAISettings(**openai_settings_kwargs),
        )

        # Initialize MCP app with settings
        self.app = MCPApp(name="agent_executor", settings=settings)

    def _resolve_provider_config(self,
                                 api_key: Optional[str],
                                 model: Optional[str],
                                 base_url: Optional[str],
                                 default_headers: Optional[Dict[str, str]]) -> Dict[
        str, Optional[Union[str, Dict[str, str]]]]:
        """Derive OpenAI-compatible client configuration for the selected provider."""
        provider = self.provider
        if provider == "blackbox":
            resolved_api_key = api_key or os.getenv("BLACKBOX_API_KEY")
            resolved_base_url = base_url or os.getenv("BLACKBOX_BASE_URL", "https://api.blackbox.ai/v1")
            resolved_model = model or os.getenv("BLACKBOX_DEFAULT_MODEL", "blackboxai/google/gemini-2.5-pro")
            resolved_headers = default_headers
            key_hint = "BLACKBOX_API_KEY"
        elif provider == "openai":
            resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
            resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL")
            resolved_model = model or os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o")
            resolved_headers = default_headers
            key_hint = "OPENAI_API_KEY"
        elif provider == "openrouter":
            resolved_api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            resolved_base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            resolved_model = model or os.getenv("OPENROUTER_DEFAULT_MODEL", "openrouter/google/gemini-flash-1.5")
            resolved_headers = self._build_openrouter_headers(default_headers)
            key_hint = "OPENROUTER_API_KEY"
        else:
            raise ValueError(
                f"Unsupported LLM provider '{provider}'. Supported providers are 'blackbox', 'openai', and 'openrouter'."
            )

        if not resolved_api_key:
            raise ValueError(
                f"API key is required for provider '{provider}'. Set the {key_hint} environment variable or pass api_key explicitly."
            )

        return {
            "api_key": resolved_api_key,
            "model": resolved_model,
            "base_url": resolved_base_url,
            "default_headers": resolved_headers,
        }

    def _build_openrouter_headers(self, base_headers: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Compose OpenRouter default headers from env overrides without clobbering explicit values."""
        headers = dict(base_headers) if base_headers else {}
        referer = os.getenv("OPENROUTER_HTTP_REFERER")
        title = os.getenv("OPENROUTER_X_TITLE")

        if referer:
            headers.setdefault("HTTP-Referer", referer)
        if title:
            headers.setdefault("X-Title", title)

        return headers or None

    async def _create_agent(self, server_names: List[str], app_context):
        """Create agent with access to specified servers following precise pattern from llm_agent.py"""
        agent = Agent(
            name="executor_agent",
            instruction="""You are an AI assistant with access to multiple tools and platforms. You can:
            - Generate content using AI tools (Blackbox)
            - Post and manage content on social media (Twitter, Bluesky, LinkedIn)
            - Search for information and trends
            - Create comprehensive content strategies
            
            Always choose the most appropriate tools for each task and explain your actions.""",
            server_names=server_names
        )
        return agent

    async def cleanup(self):
        """Clean up resources"""
        # mcp-agent handles cleanup automatically through context managers
        pass

    async def execute_parallel(self, prompt: str, server_names: List[str],
                               prompt_name: str = "custom_prompt") -> List[ExecutorResult]:
        """
        Execute prompt across multiple servers using LLM agent following precise llm_agent.py pattern
        
        Args:
            prompt: The prompt text to send
            server_names: List of server names to execute against  
            prompt_name: Name identifier for the prompt
            
        Returns:
            List of ExecutorResult objects with results from each server
        """
        import time
        results = []

        # Filter to valid server names
        valid_servers = []
        for server_name in server_names:
            if server_name in self._server_config:
                valid_servers.append(server_name)
            else:
                results.append(ExecutorResult(
                    prompt_name=prompt_name,
                    server_name=server_name,
                    error=f"Unknown server: {server_name}",
                    status="error"
                ))

        if not valid_servers:
            return results

        start_time = time.time()

        try:
            if not self.app:
                raise RuntimeError("MCP app not initialized")

            # Run the agent with the user message using modern pattern from llm_agent.py
            async with self.app.run() as agent_app:
                agent = await self._create_agent(valid_servers, agent_app)

                # Use the modern attach_llm pattern (settings are already configured in app)
                async with agent:
                    llm = await agent.attach_llm(OpenAIAugmentedLLM)
                    response = await llm.generate_str(prompt)

                    execution_time = time.time() - start_time

                    # Create successful result for all requested servers
                    for server_name in valid_servers:
                        results.append(ExecutorResult(
                            prompt_name=prompt_name,
                            server_name=server_name,
                            content=response,
                            status="generated",
                            execution_time=execution_time
                        ))

        except Exception as e:
            execution_time = time.time() - start_time
            # If execution fails, create error results for all servers
            for server_name in valid_servers:
                results.append(ExecutorResult(
                    prompt_name=prompt_name,
                    server_name=server_name,
                    error=str(e),
                    status="error",
                    execution_time=execution_time
                ))

        return results

    async def _execute_single_server(self, prompt: str, prompt_name: str, server_name: str) -> ExecutorResult:
        """Execute prompt on a single server using LLM agent pattern"""
        # This method is kept for compatibility but now uses the same agent-based approach
        results = await self.execute_parallel(prompt, [server_name], prompt_name)
        return results[0] if results else ExecutorResult(
            prompt_name=prompt_name,
            server_name=server_name,
            error="No results returned",
            status="error"
        )


# Global executor instance
_executor = None

SOCIAL_SERVER_NAMES = ["twitter", "bluesky", "linkedin"]


def get_executor() -> MCPAgentExecutor:
    """Get or create the global MCP agent executor instance"""
    global _executor
    if _executor is None:
        _executor = MCPAgentExecutor()
    return _executor


def update_mcp_server_env(env_updates: Dict[str, Optional[str]], server_names: Optional[List[str]] = None) -> None:
    """Update environment variables for MCP servers and refresh executor configuration."""
    target_servers = server_names or SOCIAL_SERVER_NAMES

    # Apply updates to process environment first so future executor instances inherit them
    for key, value in env_updates.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    if _executor is not None:
        _executor.update_server_env(env_updates, target_servers)


async def execute_mcp_client(
        prompt: str,
        server_names: List[str],
        prompt_name: str = "custom_prompt") -> List[ExecutorResult]:
    """
    Execute prompt across multiple servers using MCP agent
    
    Args:
        prompt: The prompt text to send to servers
        server_names: List of server names to execute against
        config: Configuration dictionary (kept for compatibility, not used with mcp-agent)
        prompt_name: Name identifier for the prompt (for logging/tracking)
        
    Returns:
        List of ExecutorResult objects with results from each server
    """
    executor = get_executor()
    try:
        results = await executor.execute_parallel(prompt, server_names, prompt_name)
        return results
    finally:
        # Clean up resources after execution
        await executor.cleanup()


async def execute_single_server(prompt: str, server_name: str,
                                prompt_name: str = "single_prompt") -> ExecutorResult:
    """
    Execute prompt on a single server (convenience function)
    
    Args:
        prompt: The prompt text to send
        server_name: Name of the server to use
        config: Configuration dictionary (for compatibility)
        prompt_name: Name identifier for the prompt
        
    Returns:
        Single ExecutorResult object
    """
    results = await execute_mcp_client(prompt, [server_name], prompt_name)
    return results[0] if results else ExecutorResult(
        prompt_name=prompt_name,
        server_name=server_name,
        error="No results returned",
        status="error"
    )


async def execute_with_fallback(prompt: str, server_names: List[str],
                                prompt_name: str = "fallback_prompt") -> ExecutorResult:
    """
    Execute prompt with parallel execution then return first successful result
    
    Args:
        prompt: The prompt text to send
        server_names: List of server names in order of preference
        config: Configuration dictionary (for compatibility)
        prompt_name: Name identifier for the prompt
        
    Returns:
        First successful ExecutorResult, or last error if all fail
    """
    results = await execute_mcp_client(prompt, server_names, prompt_name)

    # Return first successful result
    for result in results:
        if result.content and result.status == "generated":
            return result

    # If all failed, return the first result (which should be an error)
    return results[0] if results else ExecutorResult(
        prompt_name=prompt_name,
        server_name="unknown",
        error="No servers available",
        status="error"
    )


def get_successful_results(results: List[ExecutorResult]) -> List[ExecutorResult]:
    """
    Filter executor results to only include successful ones
    
    Args:
        results: List of ExecutorResult objects
        
    Returns:
        List of successful results only
    """
    return [result for result in results if result.content and result.status == "generated"]


def get_error_summary(results: List[ExecutorResult]) -> str:
    """
    Generate a summary of errors from executor results
    
    Args:
        results: List of ExecutorResult objects
        
    Returns:
        String summary of all errors
    """
    errors = [f"{result.server_name}: {result.error}"
              for result in results if result.error]
    return "; ".join(errors) if errors else "No errors"


def get_performance_summary(results: List[ExecutorResult]) -> Dict[str, float]:
    """
    Generate performance summary from executor results
    
    Args:
        results: List of ExecutorResult objects
        
    Returns:
        Dictionary with performance metrics
    """
    successful = get_successful_results(results)
    if not successful:
        return {"total_time": 0, "fastest": 0, "slowest": 0, "average": 0}

    times = [r.execution_time for r in successful if r.execution_time]
    if not times:
        return {"total_time": 0, "fastest": 0, "slowest": 0, "average": 0}

    return {
        "total_time": max(times),  # Parallel execution time is the slowest
        "fastest": min(times),
        "slowest": max(times),
        "average": sum(times) / len(times),
        "successful_count": len(successful),
        "total_count": len(results)
    }


def validate_server_by_platform(platform: str) -> bool:
    executor = get_executor()
    server = executor._server_config.get(platform.lower())
    return server is not None
