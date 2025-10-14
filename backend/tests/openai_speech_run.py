#!/usr/bin/env python3
"""Manual run of the OpenAI MCP speech tool through the executor."""

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
        "Invoke the openai_speech tool to synthesize the sentence 'Build pipeline completed successfully.' using "
        "model 'gpt-4o-mini-tts' and voice 'alloy'. Provide repository='test-repo', commit_sha='abc123', "
        "branch='main', and summary='Test audio generation'. After the tool call, verify the response contains "
        "a 'content_id' field and report the MongoDB document ID."
    )

    results = await execute_mcp_client(prompt, ["openai"], prompt_name="openai_speech_mp3")

    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        print("Response:\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)

        # Expected response format from updated tool:
        # {
        #     "content_id": "507f1f77bcf86cd799439011",
        #     "format": "mp3",
        #     "content_type": "audio/mpeg",
        #     "size_bytes": 12345,
        #     "storage": "mongodb",
        #     "original_text": "Build pipeline completed successfully.",
        #     "model": "gpt-4o-mini-tts",
        #     "voice": "alloy"
        # }


if __name__ == "__main__":
    asyncio.run(run())
