#!/usr/bin/env python3
"""
Test script for the /generate-content endpoint

This script issues an external POST request to the FastAPI backend in order to
exercise the /generate-content route. It mirrors the payload shape that the
endpoint expects and prints the structured response so you can confirm the
integration with MongoDB and MCP executors.
"""

import asyncio
from datetime import datetime, timezone
import json

import httpx


async def test_generate_content_endpoint(base_url: str = "http://localhost:8001") -> None:
    """Trigger /generate-content and pretty-print the response."""

    payload = {
        "repository": "example/repo",
        "commit_sha": "abc123def456",
        "branch": "main",
        "summary": "You can now edit your previous messages!",
        "product_description": "A collaborative editor that supports draft revisions.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    print("Sending request to /generate-content...")
    print(f"POST {base_url}/generate-content")
    print("Payload:")
    print(json.dumps(payload, indent=2))

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/generate-content",
                json=payload,
            )

        print(f"\nResponse status: {response.status_code}")
        print("Response headers:")
        print(json.dumps(dict(response.headers), indent=2))

        try:
            body = response.json()
            print("\nResponse body:")
            print(json.dumps(body, indent=2))

            if response.status_code == 200:
                print("\n[OK] Request succeeded!")
                print(f"Summary ID: {body.get('summary_id')}")
                print(f"Processed prompts: {len(body.get('results', []))}")
            else:
                print("\n[ERROR] Request failed; see details above.")
        except json.JSONDecodeError:
            print("\n[ERROR] Response body is not valid JSON:")
            print(response.text)

    except Exception as exc:  # pragma: no cover - diagnostic output only
        print(f"\n[ERROR] Error calling /generate-content: {exc}")


if __name__ == "__main__":
    print("Make sure the FastAPI server is running before executing this script.")
    asyncio.run(test_generate_content_endpoint())
