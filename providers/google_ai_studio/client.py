"""Google AI Studio provider implementation."""

from typing import Any

from providers.base import ProviderConfig
from providers.openai_compat import OpenAICompatibleProvider

from .request import build_request_body

GOOGLE_AI_STUDIO_DEFAULT_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)


class GoogleAIStudioProvider(OpenAICompatibleProvider):
    """Google AI Studio provider using OpenAI-compatible API for Gemini models."""

    def __init__(self, config: ProviderConfig):
        super().__init__(
            config,
            provider_name="GOOGLE_AI_STUDIO",
            base_url=config.base_url or GOOGLE_AI_STUDIO_DEFAULT_BASE_URL,
            api_key=config.api_key,
        )

    def _build_request_body(self, request: Any) -> dict:
        """Internal helper for tests and shared building."""
        return build_request_body(request)
