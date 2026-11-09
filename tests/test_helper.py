"""Offline checks for the helper's handling of untrusted protocol responses."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / "skills/brickfact-shopping/scripts/brickfact.py"
SPEC = importlib.util.spec_from_file_location("brickfact_helper", HELPER)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class Opener:
    def __init__(self, *replies):
        self.replies = iter(replies)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        value = next(self.replies)
        return Reply(value if isinstance(value, bytes) else json.dumps(value).encode())


class HelperTests(unittest.TestCase):
    def test_protocol_error_is_not_returned_as_catalogue_data(self):
        opener = Opener({"jsonrpc": "2.0", "id": 2, "error": {"code": -32602, "message": "invalid market"}})
        with self.assertRaisesRegex(ValueError, "MCP error"):
            helper.rpc(opener, "tools/call", {}, 2)

    def test_unrelated_response_is_rejected(self):
        opener = Opener({"jsonrpc": "2.0", "id": 999, "result": {"offers": []}})
        with self.assertRaisesRegex(ValueError, "Unexpected MCP response"):
            helper.rpc(opener, "tools/call", {}, 2)

    def test_oversized_response_is_rejected(self):
        with patch.object(helper, "MAX_RESPONSE", 64):
            with self.assertRaisesRegex(ValueError, "size limit"):
                helper.rpc(Opener(b"x" * 65), "tools/list", {}, 2)

    def test_tool_failure_exits_without_printing_success_data(self):
        opener = Opener(
            {"id": 1, "result": {"protocolVersion": "2025-03-26"}},
            {"id": 2, "result": {"isError": True, "content": [{"type": "text", "text": "temporarily unavailable"}]}},
        )
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("sys.argv", ["brickfact.py", "call", "search_sets", '{"market":"DE"}']):
            with patch.object(helper.urllib.request, "build_opener", return_value=opener):
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    self.assertEqual(helper.main(), 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("temporarily unavailable", stderr.getvalue())

    def test_redirects_are_not_followed(self):
        with self.assertRaisesRegex(ValueError, "Unexpected redirect"):
            helper.NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://example.com")

    def test_invalid_arguments_fail_before_network_access(self):
        with patch("sys.argv", ["brickfact.py", "call", "search_sets", "[]"]):
            with patch.object(helper.urllib.request, "build_opener") as build:
                with self.assertRaisesRegex(ValueError, "JSON object"):
                    helper.main()
                build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
