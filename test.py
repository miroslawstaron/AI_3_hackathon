#!/usr/bin/env python3  # Shebang for direct execution via system Python interpreter

"""
Real tests with assertions for model endpoints.

- Uses unittest (stdlib) with network-safe skips.
- Asserts successful HTTP 200, valid JSON shape, and non-empty code-like content.
"""

import json  # JSON encode/decode for request payloads and response parsing
import re  # Regular expressions to heuristically detect C-like code in responses
import unittest  # Standard library testing framework for organizing and asserting tests
from typing import Dict, Any  # Type hints for readability and tooling support

import requests  # HTTP client used to call the model endpoints


# Prompt messages sent to the chat endpoints; system defines behavior, user provides the task
MESSAGES = [  # List of role/content dicts forming the conversation
    {
        "role": "system",  # System prompt role, sets assistant behavior
        "content": (  # Instruction text guiding the model to output C code only
            "You are a software that writes C programs based on prompts. "
            "Provides only the code, no description."
        ),
    },
    {"role": "user", "content": "Generate a Fibonacci code"},  # User asks to generate Fibonacci implementation
]

# HTTP headers declaring JSON content-type for the API
HEADERS = {"Content-Type": "application/json"}


class ModelEndpointTests(unittest.TestCase):  # TestCase grouping tests for each endpoint/model pair
    maxDiff = None  # Allow full diffs in assertion error messages for easier debugging

    @staticmethod  # Utility not depending on instance state; helps reuse across tests
    def _payload(model: str) -> Dict[str, Any]:  # Build standard request payload for a given model name
        return {
            "model": model,  # Model identifier to query at the endpoint
            "messages": MESSAGES,  # Conversation context defined above
            "stream": False,  # Request non-streaming response for simpler validation
            "temperature": 0.0,  # Deterministic output to stabilize test expectations
        }

    def post_and_validate(self, url: str, data: Dict[str, Any]) -> str:  # Helper to POST and validate a typical chat response
        try:  # Network operations may fail; we handle exceptions to skip rather than fail the suite
            resp = requests.post(  # Perform HTTP POST to the chat endpoint
                url, data=json.dumps(data), headers=HEADERS, timeout=20  # Serialize payload, set headers, limit wait time
            )
        except requests.exceptions.RequestException as e:  # Catch connection errors, timeouts, DNS, etc.
            self.skipTest(f"Endpoint not reachable: {url} ({e})")  # Mark test as skipped when infra is unavailable

        self.assertEqual(  # Ensure the endpoint returns success status
            resp.status_code,
            200,
            msg=f"HTTP {resp.status_code} from {url}: {resp.text[:200]}",  # Include short body excerpt for diagnostics
        )

        try:
            body = resp.json()  # Parse JSON body into a Python object
        except ValueError:  # JSON decoding failed (invalid or non-JSON response)
            self.fail(f"Invalid JSON from {url}: {resp.text[:200]}")  # Treat invalid JSON as a test failure

        self.assertIsInstance(body, dict)  # Top-level response should be a dict
        self.assertIn("message", body)  # Expect 'message' key according to API schema
        self.assertIsInstance(body["message"], dict)  # 'message' should itself be a dict
        self.assertIn("content", body["message"])  # 'content' holds the generated text/code

        content = body["message"]["content"]  # Extract generated content string
        self.assertIsInstance(content, str)  # Content must be textual
        self.assertGreater(len(content.strip()), 0, msg="Empty content returned")  # Must not be empty/whitespace

        # Heuristic: require signals typical for C code to ensure the model returned code, not prose
        code_like = bool(
            re.search(r"#include\s*<[^>]+>", content)  # C header include line
            or re.search(r"\bint\s+main\s*\(", content)  # Main function signature
            or ";" in content  # Statement terminators common in C
        )
        self.assertTrue(  # Fail if content does not look like C code
            code_like, msg=f"Content does not look like C code: {content[:200]}"
        )
        return content  # Return content for callers that may want further checks

    def test_deepthought_llama32(self):  # Validate llama3.2:latest on deepthought endpoint
        url = "http://deepthought.cse.chalmers.se:80/api/chat"  # Base URL for deepthought service
        data = self._payload("llama3.2:latest")  # Compose request payload for specified model
        _ = self.post_and_validate(url, data)  # Execute and verify response meets expectations

    def test_deeperthought_llama32(self):  # Validate llama3.2:latest on deeperthought endpoint
        url = "http://deeperthought.cse.chalmers.se:80/api/chat"  # Base URL for deeperthought service
        data = self._payload("llama3.2:latest")  # Compose request payload for specified model
        _ = self.post_and_validate(url, data)  # Execute and verify response meets expectations

    def test_deepestthought_gemma3(self):  # Validate gemma3:latest on deepestthought endpoint
        url = "http://deepestthought.cse.chalmers.se:11434/api/chat"  # Base URL (non-standard port) for deepestthought service
        data = self._payload("gemma3:latest")  # Compose request payload for specified model
        _ = self.post_and_validate(url, data)  # Execute and verify response meets expectations

    def test_lazythought_gpt_oss(self):  # Validate gpt-oss:20b on lazythought endpoint
        url = "http://lazythought.cse.chalmers.se:80/api/chat"  # Base URL for lazythought service
        data = self._payload("gpt-oss:20b")  # Compose request payload for specified model
        _ = self.post_and_validate(url, data)  # Execute and verify response meets expectations


if __name__ == "__main__":  # Allow running this module directly to execute tests
    unittest.main(verbosity=2)  # Invoke unittest test runner with verbose test names