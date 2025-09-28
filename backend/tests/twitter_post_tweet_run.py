#!/usr/bin/env python3
"""Manual run for the Twitter MCP post_tweet tool via the executor."""

import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from executor import execute_mcp_client

REQUIRED_ENV_VARS = [
    "API_KEY",
    "API_SECRET_KEY",
    "ACCESS_TOKEN",
    "ACCESS_TOKEN_SECRET",
]


def _provider_fallback() -> str:
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("BLACKBOX_API_KEY"):
        return "blackbox"
    return "openai"


def _validate_env() -> bool:
    missing = [key for key in REQUIRED_ENV_VARS if not os.getenv(key)]
    if missing:
        print("Missing Twitter credentials:", ", ".join(missing))
        return False
    return True


async def run() -> None:
    if not _validate_env():
        return

    os.environ.setdefault("MCP_LLM_PROVIDER", _provider_fallback())

    prompt = (
        "Use the twitter post_tweet tool with text 'Testing MCP Twitter integration #DevTools'. "
        "After you execute the tool, respond with the tweet URL only."
    )

    results = await execute_mcp_client(prompt, ["twitter"], prompt_name="twitter_post_tweet")
    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        if result.content:
            print("Response:\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)


if __name__ == "__main__":
    asyncio.run(run())
