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
        "model 'gpt-4o-mini-tts', voice 'alloy', response_format 'mp3'. After the tool call, respond with valid JSON "
        "containing keys 'audio_base64', 'format', and 'size_bytes' copied directly from the tool output."
    )

    results = await execute_mcp_client(prompt, ["openai"], prompt_name="openai_speech_mp3")

    for result in results:
        print(f"\nServer: {result.server_name}")
        print(f"Status: {result.status}")
        if result.content:
            try:
                parsed = json.loads(result.content)
                print("Format:", parsed.get("format"))
                print("Size bytes:", parsed.get("size_bytes"))
                preview = parsed.get("audio_base64", "")[:80]
                print("Audio preview (first 80 chars):", preview)
            except json.JSONDecodeError:
                print("Raw response (not JSON):\n" + result.content)
        if result.error:
            print("Error:\n" + result.error)


if __name__ == "__main__":
    asyncio.run(run())
