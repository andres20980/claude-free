"""Tests for the OpenAICompatibleProvider base class."""

from typing import ClassVar

import pytest

from providers.base import ProviderConfig
from providers.openai_compat import OpenAICompatibleProvider


class DummyOpenAICompatibleProvider(OpenAICompatibleProvider):
    """Concrete subclass for testing."""

    def _build_request_body(self, request):
        # Minimal body for testing
        return {
            "model": request.model,
            "messages": request.messages,
            "stream": True,
        }


class FakeRequest:
    model: ClassVar[str] = "test-model"
    messages: ClassVar[list[dict[str, str]]] = [{"role": "user", "content": "hi"}]


@pytest.fixture
def provider_config():
    return ProviderConfig(
        api_key="test-key",
        rate_limit=10,
        rate_window=10,
        max_concurrency=2,
        http_read_timeout=30,
        http_write_timeout=5,
        http_connect_timeout=2,
    )


def test_provider_initialization(provider_config):
    provider = DummyOpenAICompatibleProvider(
        config=provider_config,
        provider_name="dummy",
        base_url="https://example.com/v1",
        api_key="test-key",
    )
    assert provider._provider_name == "dummy"
    assert provider._base_url == "https://example.com/v1"
    assert provider._api_key == "test-key"


def test_build_request_body_called(provider_config):
    provider = DummyOpenAICompatibleProvider(
        config=provider_config,
        provider_name="dummy",
        base_url="https://example.com/v1",
        api_key="test-key",
    )

    req = FakeRequest()
    body = provider._build_request_body(req)
    assert body["model"] == "test-model"
    assert body["messages"] == [{"role": "user", "content": "hi"}]
    assert body["stream"] is True
