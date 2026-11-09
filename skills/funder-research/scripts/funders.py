#!/usr/bin/env python3
"""Dependency-free client for the public, read-only Plutus directory.

Uses this endpoint's stateless JSON transport, not a general MCP client.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://plutusai.net/mcp/funders"


def unwrap(envelope):
    if "error" in envelope or "result" not in envelope:
        raise ValueError("MCP error or missing result: " + json.dumps(envelope))
    result = envelope["result"]
    if result.get("isError"):
        raise ValueError("Tool error: " + json.dumps(result))
    if "structuredContent" in result:
        return result["structuredContent"]
    if "tools" in result:
        return result
    for item in result.get("content", []):
        if item.get("type") == "text":
            return json.loads(item["text"])
    raise ValueError("Missing structured or JSON-text result")


def call(name, arguments):
    if name not in ("list", "search_funders", "get_funder") or not isinstance(arguments, dict):
        raise ValueError("Only list/search_funders/get_funder with JSON object arguments are allowed")
    payload = {"jsonrpc": "2.0", "id": 1,
               "method": "tools/list" if name == "list" else "tools/call",
               "params": {} if name == "list" else {"name": name, "arguments": arguments}}
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers={
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
        "User-Agent": "plutus-funder-research/1.0"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return unwrap(json.load(response))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=["list", "search_funders", "get_funder"])
    parser.add_argument("arguments", nargs="?", default="{}", help="JSON object; never include private data")
    args = parser.parse_args()
    try:
        print(json.dumps(call(args.tool, json.loads(args.arguments)), indent=2, ensure_ascii=False))
    except (ValueError, urllib.error.URLError, TimeoutError) as error:
        print("Directory request failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
