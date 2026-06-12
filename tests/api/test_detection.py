"""Edge case tests for api/detection.py."""

from unittest.mock import patch

from api.detection import (
    is_filepath_extraction_request,
    is_models_request,
    is_prefix_detection_request,
)
from api.models.anthropic import Message, MessagesRequest


def _make_request(content: str, **kwargs) -> MessagesRequest:
    return MessagesRequest(
        model="claude-3-sonnet",
        max_tokens=100,
        messages=[Message(role="user", content=content)],
        **kwargs,
    )


class TestIsPrefixDetectionRequest:
    def test_output_marker_handling(self):
        """Content with Command: but Output: after cmd_start; output has < or \\n\\n."""
        content = "<policy_spec> Command:\nls -la\nOutput:\na.txt\nb.txt\n\nmore"
        req = _make_request(content)
        is_req, cmd = is_prefix_detection_request(req)
        assert is_req is True
        assert "ls -la" in cmd

    def test_prefix_detection_with_empty_command_section(self):
        """Command: at end with no content returns empty command."""
        req = _make_request("<policy_spec> Command: ")
        is_req, cmd = is_prefix_detection_request(req)
        assert is_req is True
        assert cmd == ""

    def test_exception_in_try_returns_false(self):
        """Exception in try block (e.g. content slice) returns False, ''."""
        req = _make_request("<policy_spec> Command: x")

        # Return object that raises when sliced - triggers except in is_prefix_detection_request
        class BadStr(str):
            def __getitem__(self, key):
                raise TypeError("bad slice")

        with patch(
            "api.detection.extract_text_from_content",
            return_value=BadStr("<policy_spec> Command: x"),
        ):
            is_req, cmd = is_prefix_detection_request(req)
        assert is_req is False
        assert cmd == ""


class TestIsFilepathExtractionRequest:
    def test_output_marker_minus_one_returns_false(self):
        """Output: not found after Command: returns False."""
        content = "Command:\nls\nfilepaths"
        req = _make_request(content)
        is_fp, cmd, out = is_filepath_extraction_request(req)
        assert is_fp is False
        assert cmd == ""
        assert out == ""

    def test_output_has_angle_bracket_splits(self):
        """Output containing < is split and first part used."""
        content = "Command:\nls\nOutput:\na.txt b.txt <extra>\nfilepaths"
        req = _make_request(content)
        is_fp, _cmd, out = is_filepath_extraction_request(req)
        assert is_fp is True
        assert "<" not in out
        assert out == "a.txt b.txt"

    def test_output_has_double_newline_splits(self):
        """Output containing \\n\\n is split and first part used."""
        content = "Command:\nls\nOutput:\na.txt\nb.txt\n\nmore text\nfilepaths"
        req = _make_request(content)
        is_fp, _cmd, out = is_filepath_extraction_request(req)
        assert is_fp is True
        assert "more" not in out


class TestIsModelsRequest:
    def test_returns_true_for_model_listing_phrases(self):
        """Should return true for common model listing phrases."""
        test_cases = [
            "list models",
            "available models",
            "show models",
            "what models are available",
            "models available",
            "/models",
            "model list",
            "List Models",  # Case insensitive
            "AVAILABLE MODELS",
        ]

        for content in test_cases:
            req = _make_request(content)
            assert is_models_request(req) is True, f"Failed for content: {content}"

    def test_returns_false_for_non_model_requests(self):
        """Should return false for requests that don't look like model listings."""
        test_cases = [
            "hello world",
            "how are you?",
            "what's the weather?",
            "can you help me code?",
            "quota check",  # This is for quota detection, not models
            "",  # Empty string
            "Command: ls\nOutput: file.txt",  # This is for filepath detection
        ]

        for content in test_cases:
            req = _make_request(content)
            assert is_models_request(req) is False, f"Failed for content: {content}"

    def test_returns_false_for_wrong_structure(self):
        """Should return false if message structure is wrong."""
        # Multiple messages
        req = MessagesRequest(
            model="claude-3-sonnet",
            max_tokens=100,
            messages=[
                Message(role="user", content="list models"),
                Message(role="assistant", content="Here are the models..."),
            ],
        )
        assert is_models_request(req) is False

        # Non-user message
        req = MessagesRequest(
            model="claude-3-sonnet",
            max_tokens=100,
            messages=[Message(role="assistant", content="list models")],
        )
        assert is_models_request(req) is False

        # No messages
        req = MessagesRequest(model="claude-3-sonnet", max_tokens=100, messages=[])
        assert is_models_request(req) is False
