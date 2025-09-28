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
        "Call the openai_image tool with prompt 'Minimal line icon representing CI success', model 'gpt-image-1', "
        "n=1, response_format='b64_json'. After you receive the tool result, reply ONLY with valid JSON containing "
        "one key 'image' whose value is the base64 string from the tool response."
    )

    results = await execute_mcp_client(prompt, ["openai"], prompt_name="openai_image_icon")

    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        if result.content:
            try:
                parsed = json.loads(result.content)
                print("Decoded JSON keys:", ", ".join(parsed.keys()))
                print("Sample payload (first 80 chars):", parsed.get("image", "")[:80])
            except json.JSONDecodeError:
                print("Raw response (not JSON):\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)


if __name__ == "__main__":
    asyncio.run(run())
