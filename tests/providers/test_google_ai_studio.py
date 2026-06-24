"""Tests for Google AI Studio provider."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from providers.base import ProviderConfig
from providers.google_ai_studio import GoogleAIStudioProvider
from providers.google_ai_studio.request import GEMINI_DEFAULT_MAX_TOKENS


class MockMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content


class MockRequest:
    def __init__(self, **kwargs):
        self.model = "gemini-2.5-flash"
        self.messages = [MockMessage("user", "Hello")]
        self.max_tokens = 100
        self.temperature = 0.5
        self.top_p = 0.9
        self.system = "System prompt"
        self.stop_sequences = None
        self.tools = []
        self.extra_body = {}
        self.thinking = MagicMock()
        self.thinking.enabled = True
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def google_config():
    return ProviderConfig(
        api_key="gemini-key",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        rate_limit=10,
        rate_window=60,
    )


@pytest.fixture(autouse=True)
def mock_rate_limiter():
    """Mock the global rate limiter to prevent waiting."""
    with patch("providers.openai_compat.GlobalRateLimiter") as mock:
        instance = mock.get_instance.return_value
        instance.wait_if_blocked = AsyncMock(return_value=False)

        async def _passthrough(fn, *args, **kwargs):
            return await fn(*args, **kwargs)

        instance.execute_with_retry = AsyncMock(side_effect=_passthrough)
        yield instance


@pytest.fixture
def google_provider(google_config):
    return GoogleAIStudioProvider(google_config)


def test_init(google_config):
    """Test provider initialization."""
    with patch("providers.openai_compat.AsyncOpenAI") as mock_openai:
        provider = GoogleAIStudioProvider(google_config)
        assert provider._api_key == "gemini-key"
        assert (
            provider._base_url
            == "https://generativelanguage.googleapis.com/v1beta/openai"
        )
        mock_openai.assert_called_once()


def test_build_request_body_default_max_tokens(google_provider):
    """max_tokens=None or 0 uses GEMINI_DEFAULT_MAX_TOKENS."""
    req = MockRequest(max_tokens=None)
    body = google_provider._build_request_body(req)
    assert body["max_tokens"] == GEMINI_DEFAULT_MAX_TOKENS
    assert body["max_tokens"] == 8192


@pytest.mark.asyncio
async def test_stream_response_text(google_provider):
    """Test streaming text response."""
    req = MockRequest()

    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [
        MagicMock(
            delta=MagicMock(content="Hello", reasoning_content=None),
            finish_reason=None,
        )
    ]
    mock_chunk1.usage = None

    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [
        MagicMock(
            delta=MagicMock(content=" World", reasoning_content=None),
            finish_reason="stop",
        )
    ]
    mock_chunk2.usage = MagicMock(completion_tokens=10)

    # A tiny helper to avoid nested async generators
    class MockAsyncIterator:
        def __init__(self, items):
            self.items = items
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index >= len(self.items):
                raise StopAsyncIteration
            item = self.items[self.index]
            self.index += 1
            return item

    with patch.object(
        google_provider._client.chat.completions, "create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = MockAsyncIterator([mock_chunk1, mock_chunk2])

        events = [e async for e in google_provider.stream_response(req)]

        assert len(events) > 0
        assert "event: message_start" in events[0]

        text_content = ""
        for e in events:
            if "event: content_block_delta" in e and '"text_delta"' in e:
                for line in e.splitlines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "delta" in data and "text" in data["delta"]:
                            text_content += data["delta"]["text"]

        assert "Hello World" in text_content
