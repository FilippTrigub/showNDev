#!/usr/bin/env python3
"""Manual run for the Twitter MCP post_thread tool via the executor."""

import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from executor import execute_mcp_client

REQUIRED_ENV_VARS = [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET_KEY",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET",
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
        "Use the twitter post_thread tool to publish a two-part update. "
        "Tweet 1: 'Thread test part 1 – building MCP integrations'. "
        "Tweet 2: 'Thread test part 2 – follow @example for updates'. "
        "After posting, summarize the URLs returned."
    )

    results = await execute_mcp_client(prompt, ["twitter"], prompt_name="twitter_post_thread")
    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        if result.content:
            print("Response:\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)


if __name__ == "__main__":
    asyncio.run(run())
