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
        "Use the openai_chat tool with model 'gpt-4o-mini' to craft a single release-note sentence announcing "
        "the new analytics dashboard. Include messages with role 'user' asking for the sentence. "
        "Also provide repository='test-repo', commit_sha='abc123', branch='main', "
        "summary='Test text generation', and persist_to_db=True. After the tool call, verify the response "
        "contains a 'content_id' field and 'text' field, then report both the MongoDB document ID and the "
        "generated sentence."
    )

    results = await execute_mcp_client(prompt, ["openai"], prompt_name="openai_chat_sentence")

    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        if result.content:
            print("Response:\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)

        # Expected response format from updated tool:
        # {
        #     "content_id": "507f1f77bcf86cd799439013",
        #     "text": "Introducing our new analytics dashboard...",
        #     "model": "gpt-4o-mini",
        #     "storage": "mongodb",
        #     "message_count": 1,
        #     "response_length": 89
        # }


if __name__ == "__main__":
    asyncio.run(run())
