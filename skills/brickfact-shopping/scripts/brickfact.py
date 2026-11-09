#!/usr/bin/env python3
"""Read public Brickfact catalogue data over stateless MCP; no dependencies."""

import argparse
import json
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://mcp.brickfact.com/mcp"
PROTOCOL = "2025-03-26"
TOOLS = frozenset({
    "search_sets", "get_set_details", "get_set_offers", "compare_sets",
    "get_price_history", "list_themes", "get_retail_price_history",
    "assess_deal", "find_alternatives", "render_sets", "get_app_handoff",
})
MAX_RESPONSE = 4 * 1024 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Unexpected redirect from Brickfact; request stopped")


def rpc(opener, method, params, request_id, protocol=PROTOCOL):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": request_id, "method": method, "params": params,
    }, allow_nan=False).encode()
    if len(payload) > 32 * 1024:
        raise ValueError("Request exceeds Brickfact's 32 KiB input limit")
    request = urllib.request.Request(ENDPOINT, data=payload, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": protocol,
        "User-Agent": "brickfact-shopping-skill/1.0.0",
    })
    with opener.open(request, timeout=30) as response:
        raw = response.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE:
        raise ValueError("Brickfact response exceeded the size limit")
    envelope = json.loads(raw)
    if not isinstance(envelope, dict) or envelope.get("id") != request_id:
        raise ValueError("Unexpected MCP response")
    if "error" in envelope:
        raise ValueError("MCP error: " + json.dumps(envelope["error"]))
    if "result" not in envelope:
        raise ValueError("MCP response is missing a result")
    return envelope["result"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    discovery = commands.add_parser("tools", help="List current tool schemas")
    discovery.add_argument("name", nargs="?", choices=sorted(TOOLS))
    call = commands.add_parser("call", help="Call a read-only catalogue tool")
    call.add_argument("name", choices=sorted(TOOLS))
    call.add_argument("arguments", help="JSON object matching the tool schema")
    args = parser.parse_args()
    arguments = None
    if args.command == "call":
        arguments = json.loads(args.arguments)
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object")

    # Fixed origin, TLS verification, no environment proxy or redirect forwarding.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    init = rpc(opener, "initialize", {
        "protocolVersion": PROTOCOL, "capabilities": {},
        "clientInfo": {"name": "brickfact-shopping-skill", "version": "1.0.0"},
    }, 1)
    protocol = init.get("protocolVersion")
    if not isinstance(protocol, str):
        raise ValueError("Server did not negotiate an MCP protocol version")
    if args.command == "tools":
        result = rpc(opener, "tools/list", {}, 2, protocol)
        tools = result["tools"]
        if args.name:
            tools = [tool for tool in tools if tool["name"] == args.name]
            if not tools:
                raise ValueError("Tool is not available on the current server")
        print(json.dumps({"tools": tools}, ensure_ascii=False, indent=2))
    else:
        result = rpc(opener, "tools/call", {"name": args.name, "arguments": arguments}, 2, protocol)
        if result.get("isError"):
            print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        print(json.dumps(result.get("structuredContent", result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as exc:
        retry = exc.headers.get("Retry-After")
        suffix = f"; retry after {retry} seconds" if retry else ""
        print(f"Brickfact HTTP {exc.code}{suffix}. Data is unavailable; do not invent results.", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Brickfact request failed: {exc}", file=sys.stderr)
        sys.exit(1)
