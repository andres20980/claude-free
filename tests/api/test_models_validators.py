from unittest.mock import patch

import pytest

from api.models.anthropic import Message, MessagesRequest, TokenCountRequest
from config.settings import Settings


@pytest.fixture
def mock_settings():
    settings = Settings()
    settings.model = "nvidia_nim/target-model-from-settings"
    settings.model_opus = None
    settings.model_sonnet = None
    settings.model_haiku = None
    return settings


def test_messages_request_map_model_claude_to_default(mock_settings):
    with patch("api.models.anthropic.get_settings", return_value=mock_settings):
        request = MessagesRequest(
            model="claude-3-opus",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )

        assert request.model == "target-model-from-settings"
        assert request.original_model == "claude-3-opus"


def test_messages_request_map_model_with_provider_prefix(mock_settings):
    with patch("api.models.anthropic.get_settings", return_value=mock_settings):
        request = MessagesRequest(
            model="anthropic/claude-3-haiku",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )

        assert request.model == "target-model-from-settings"


def test_token_count_request_model_validation(mock_settings):
    with patch("api.models.anthropic.get_settings", return_value=mock_settings):
        request = TokenCountRequest(
            model="claude-3-sonnet", messages=[Message(role="user", content="hello")]
        )

        assert request.model == "target-model-from-settings"


def test_messages_request_model_mapping_logs(mock_settings):
    with (
        patch("api.models.anthropic.get_settings", return_value=mock_settings),
        patch("api.models.anthropic.logger.debug") as mock_log,
    ):
        MessagesRequest(
            model="claude-2.1",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )

        mock_log.assert_called()
        args = mock_log.call_args[0][0]
        assert "MODEL MAPPING" in args
        assert "claude-2.1" in args
        assert "target-model-from-settings" in args


def test_messages_request_resolved_provider_model_default(mock_settings):
    """resolved_provider_model is set to the full model string."""
    with patch("api.models.anthropic.get_settings", return_value=mock_settings):
        request = MessagesRequest(
            model="claude-3-opus",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )
        assert (
            request.resolved_provider_model == "nvidia_nim/target-model-from-settings"
        )


def test_messages_request_model_aware_opus_override():
    """Opus model routes to MODEL_OPUS when set."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_opus = "open_router/deepseek/deepseek-r1"

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-opus-4-20250514",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )
        assert request.model == "deepseek/deepseek-r1"
        assert request.resolved_provider_model == "open_router/deepseek/deepseek-r1"
        assert request.original_model == "claude-opus-4-20250514"


def test_messages_request_model_aware_haiku_override():
    """Haiku model routes to MODEL_HAIKU when set."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_haiku = "lmstudio/qwen2.5-7b"

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )
        assert request.model == "qwen2.5-7b"
        assert request.resolved_provider_model == "lmstudio/qwen2.5-7b"


def test_messages_request_model_aware_sonnet_override():
    """Sonnet model routes to MODEL_SONNET when set."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_sonnet = "nvidia_nim/meta/llama-3.3-70b-instruct"

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )
        assert request.model == "meta/llama-3.3-70b-instruct"
        assert (
            request.resolved_provider_model == "nvidia_nim/meta/llama-3.3-70b-instruct"
        )


def test_messages_request_model_fallback_when_not_set():
    """When model override is None, falls back to MODEL."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_opus = None
    settings.model_sonnet = None
    settings.model_haiku = None
    # model_opus is None

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-opus-4-20250514",
            max_tokens=100,
            messages=[Message(role="user", content="hello")],
        )
        assert request.model == "fallback-model"
        assert request.resolved_provider_model == "nvidia_nim/fallback-model"


def test_token_count_request_model_aware():
    """TokenCountRequest also uses model-aware resolution."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_haiku = "lmstudio/qwen2.5-7b"

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = TokenCountRequest(
            model="claude-3-haiku-20240307",
            messages=[Message(role="user", content="hello")],
        )
        assert request.model == "qwen2.5-7b"


def test_auto_model_routes_short_simple_prompt_to_haiku():
    """Auto routing sends simple prompts to MODEL_HAIKU."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_haiku = "nvidia_nim/fast-model"
    settings.model_sonnet = "nvidia_nim/coding-model"
    settings.model_opus = "nvidia_nim/deep-model"
    settings.auto_model_enabled = True

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-3-7-sonnet-latest",
            max_tokens=100,
            messages=[Message(role="user", content="hola")],
        )
        assert request.model == "fast-model"
        assert request.auto_model_tier == "haiku"
        assert request.auto_model_reason == "short_simple_prompt"


def test_auto_model_routes_code_prompt_to_sonnet():
    """Auto routing keeps normal code work on MODEL_SONNET."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_haiku = "nvidia_nim/fast-model"
    settings.model_sonnet = "nvidia_nim/coding-model"
    settings.model_opus = "nvidia_nim/deep-model"
    settings.auto_model_enabled = True

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-3-5-haiku-latest",
            max_tokens=100,
            messages=[
                Message(
                    role="user",
                    content="implementa un fix en este código y añade pytest",
                )
            ],
        )
        assert request.model == "coding-model"
        assert request.auto_model_tier == "sonnet"
        assert request.auto_model_reason == "code_or_tool_signal"


def test_auto_model_routes_deep_prompt_to_opus():
    """Auto routing promotes difficult debugging/review work to MODEL_OPUS."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_haiku = "nvidia_nim/fast-model"
    settings.model_sonnet = "nvidia_nim/coding-model"
    settings.model_opus = "nvidia_nim/deep-model"
    settings.auto_model_enabled = True

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-3-7-sonnet-latest",
            max_tokens=100,
            messages=[
                Message(
                    role="user",
                    content="haz una revisión profunda de este bug de concurrencia",
                )
            ],
        )
        assert request.model == "deep-model"
        assert request.auto_model_tier == "opus"
        assert request.auto_model_reason == "deep_signal"


def test_auto_model_manual_override_wins_and_is_stripped():
    """Manual #model directives override rules and are not sent downstream."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_haiku = "nvidia_nim/fast-model"
    settings.model_sonnet = "nvidia_nim/coding-model"
    settings.model_opus = "nvidia_nim/deep-model"
    settings.auto_model_enabled = True

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-3-7-sonnet-latest",
            max_tokens=100,
            messages=[
                Message(
                    role="user",
                    content="#model: haiku\nhaz una revisión profunda de concurrencia",
                )
            ],
        )
        assert request.model == "fast-model"
        assert request.auto_model_tier == "haiku"
        assert request.auto_model_reason == "manual_override"
        assert (
            request.messages[0].content == "haz una revisión profunda de concurrencia"
        )


def test_auto_model_opus_override_respects_allow_opus_false():
    """AUTO_MODEL_ALLOW_OPUS=false downgrades manual Opus override to Sonnet."""
    settings = Settings()
    settings.model = "nvidia_nim/fallback-model"
    settings.model_sonnet = "nvidia_nim/coding-model"
    settings.model_opus = "nvidia_nim/deep-model"
    settings.auto_model_enabled = True
    settings.auto_model_allow_opus = False

    with patch("api.models.anthropic.get_settings", return_value=settings):
        request = MessagesRequest(
            model="claude-3-5-haiku-latest",
            max_tokens=100,
            messages=[Message(role="user", content="#model: opus\nrevisa esto")],
        )
        assert request.model == "coding-model"
        assert request.auto_model_tier == "sonnet"
        assert request.auto_model_reason == "manual_opus_disabled"
