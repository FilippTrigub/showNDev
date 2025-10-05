from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from config import config
from tools import AudioTools, ImageTools, ModelTools, TextTools


mcp = FastMCP(
    name="OpenAI MCP Server",
    instructions="Expose OpenAI text, image, and audio generation capabilities via MCP tools.",
)


@mcp.tool
async def openai_chat(
    model: str,
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    instructions: Optional[str] = None,
    stream: bool = False,
) -> str:
    """Generate text using OpenAI's Responses API."""

    return await TextTools.generate_text(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        instructions=instructions,
        stream=stream,
    )


@mcp.tool
async def openai_image(
    prompt: str,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate one or more images through OpenAI's image generation endpoint."""

    return await ImageTools.generate_image(
        prompt=prompt,
        model=model,
    )


@mcp.tool
async def openai_speech(
    text: str,
    model: str,
    voice: str,
) -> Dict[str, Any]:
    """Synthesize speech audio to a temp file; follow up with MongoDB MCP tools to store it."""

    return await AudioTools.generate_speech(
        text=text,
        model=model,
        voice=voice,
    )


@mcp.tool
async def openai_models(model_type: Optional[str] = None) -> Dict[str, Any]:
    """Return a curated list of frequently used OpenAI models grouped by modality."""

    return await ModelTools.list_models(model_type)


@mcp.tool
async def test_connection() -> Dict[str, Any]:
    """Validate OpenAI connectivity by issuing a lightweight chat request."""

    try:
        ping_response = await TextTools.generate_text(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply with OK"}],
            max_output_tokens=8,
            temperature=0.0,
        )
        return {
            "status": "success",
            "message": "Connection to OpenAI API successful",
            "api_key_present": True,
            "test_response": ping_response,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Connection failed: {exc}",
            "api_key_present": bool(config.api_key),
        }


def main() -> None:
    try:
        print("Starting OpenAI MCP Server...", file=sys.stderr)
        print(f"API Key configured: {'Yes' if config.api_key else 'No'}", file=sys.stderr)
        print(f"Base URL: {config.base_url}", file=sys.stderr)
        mcp.run()
    except Exception as exc:
        print(f"Failed to start OpenAI MCP server: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
