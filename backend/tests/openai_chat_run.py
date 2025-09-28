#!/usr/bin/env python3
"""Manual run of the OpenAI MCP chat tool through the executor."""

import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from executor import execute_mcp_client


async def run() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; skipping run.")
        return

    os.environ.setdefault("MCP_LLM_PROVIDER", "openai")

    prompt = (
        "Use the openai_chat tool to craft a single release-note sentence announcing the new analytics dashboard. "
        "Return only the sentence and ensure it includes the exact phrase 'analytics dashboard'."
    )

    results = await execute_mcp_client(prompt, ["openai"], prompt_name="openai_chat_sentence")

    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        if result.content:
            print("Response:\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)


if __name__ == "__main__":
    asyncio.run(run())
