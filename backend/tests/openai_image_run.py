#!/usr/bin/env python3
"""Manual run of the OpenAI MCP image tool through the executor."""

import asyncio
import json
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
        "Call the openai_image tool with prompt 'Minimal line icon representing CI success', "
        "model 'dall-e-3', repository='test-repo', commit_sha='abc123', branch='main', "
        "and summary='Test image generation'. After you receive the tool result, verify the response "
        "contains a 'content_id' field and 'image_urls' array, then report the MongoDB document ID "
        "and image URL(s)."
    )

    results = await execute_mcp_client(prompt, ["openai"], prompt_name="openai_image_icon")

    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        print("Response:\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)

        # Expected response format from updated tool:
        # {
        #     "content_id": "507f1f77bcf86cd799439012",
        #     "image_urls": ["https://..."],
        #     "prompt": "Minimal line icon representing CI success",
        #     "model": "dall-e-3",
        #     "storage": "mongodb",
        #     "image_count": 1
        # }


if __name__ == "__main__":
    asyncio.run(run())
