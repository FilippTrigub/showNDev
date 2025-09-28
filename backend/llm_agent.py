#!/usr/bin/env python3
"""Manual MCP agent tester.

This utility sends a single prompt through the MCP agent pipeline so you can
quickly verify each configured server (including the OpenAI server) is wired up
correctly.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from executor import ExecutorResult, execute_mcp_client, get_error_summary


DEFAULT_SERVERS = ["mongodb"]

# Load environment variables from the local .env, if present.
load_dotenv(".env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a prompt against MCP servers for manual testing.")
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send. If omitted, the script will prompt for input interactively.",
    )
    parser.add_argument(
        "-s",
        "--servers",
        nargs="+",
        default=DEFAULT_SERVERS,
        help=f"Servers to target (default: {' '.join(DEFAULT_SERVERS)}).",
    )
    parser.add_argument(
        "-n",
        "--prompt-name",
        default="manual_test",
        help="Identifier recorded with the request (default: manual_test).",
    )
    return parser.parse_args()


async def run_prompt(prompt: str, servers: List[str], prompt_name: str) -> List[ExecutorResult]:
    if not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    print("Running prompt with servers:", ", ".join(servers))
    results = await execute_mcp_client(prompt, servers, prompt_name=prompt_name)
    return results


def render_results(results: List[ExecutorResult]) -> None:
    if not results:
        print("No results returned. Check server configuration.")
        return

    for result in results:
        header = f"[{result.server_name}] {result.status.upper()}"
        print("\n" + header)
        print("-" * len(header))
        if result.content:
            print(result.content)
        if result.error:
            print(f"Error: {result.error}")
        if result.execution_time is not None:
            print(f"Execution time: {result.execution_time:.2f}s")

    errors = [r for r in results if r.error]
    if errors:
        print("\nSummary of errors:")
        print(get_error_summary(results))


async def async_main() -> None:
    args = parse_args()
    prompt = args.prompt or input("Enter prompt: ")

    try:
        results = await run_prompt(prompt, args.servers, args.prompt_name)
    except Exception as exc:
        print(f"Failed to run prompt: {exc}")
        return

    render_results(results)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
