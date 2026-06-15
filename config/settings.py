"""Centralized configuration using Pydantic Settings."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, cast

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .model_router import ModelRoutingDecision, ModelTier, route_model_tier
from .nim import NimSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ==================== OpenRouter Config ====================
    open_router_api_key: str = Field(default="", validation_alias="OPENROUTER_API_KEY")

    # ==================== Messaging Platform Selection ====================
    # Valid: "telegram" | "discord"
    messaging_platform: str = Field(
        default="discord", validation_alias="MESSAGING_PLATFORM"
    )

    # ==================== NVIDIA NIM Config ====================
    nvidia_nim_api_key: str = ""

    # ==================== LM Studio Config ====================
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        validation_alias="LM_STUDIO_BASE_URL",
    )

    # ==================== Model ====================
    # All Claude model requests are mapped to this single model (fallback)
    # Format: provider_type/model/name
    model: str = "nvidia_nim/meta/llama3-70b-instruct"

    # Per-model overrides (optional, falls back to MODEL)
    # Each can use a different provider
    model_opus: str | None = Field(default=None, validation_alias="MODEL_OPUS")
    model_sonnet: str | None = Field(default=None, validation_alias="MODEL_SONNET")
    model_haiku: str | None = Field(default=None, validation_alias="MODEL_HAIKU")
    model_fallbacks: list[str] = Field(
        default_factory=list, validation_alias="MODEL_FALLBACKS"
    )
    model_opus_fallbacks: list[str] = Field(
        default_factory=list, validation_alias="MODEL_OPUS_FALLBACKS"
    )
    model_sonnet_fallbacks: list[str] = Field(
        default_factory=list, validation_alias="MODEL_SONNET_FALLBACKS"
    )
    model_haiku_fallbacks: list[str] = Field(
        default_factory=list, validation_alias="MODEL_HAIKU_FALLBACKS"
    )

    # ==================== Automatic Model Routing ====================
    auto_model_enabled: bool = Field(
        default=False, validation_alias="AUTO_MODEL_ENABLED"
    )
    auto_model_default: ModelTier = Field(
        default="sonnet", validation_alias="AUTO_MODEL_DEFAULT"
    )
    auto_model_allow_opus: bool = Field(
        default=True, validation_alias="AUTO_MODEL_ALLOW_OPUS"
    )
    auto_model_strip_override: bool = Field(
        default=True, validation_alias="AUTO_MODEL_STRIP_OVERRIDE"
    )
    auto_model_debug: bool = Field(default=False, validation_alias="AUTO_MODEL_DEBUG")

    # ==================== Provider Rate Limiting ====================
    provider_rate_limit: int = Field(default=40, validation_alias="PROVIDER_RATE_LIMIT")
    provider_rate_window: int = Field(
        default=60, validation_alias="PROVIDER_RATE_WINDOW"
    )
    provider_max_concurrency: int = Field(
        default=5, validation_alias="PROVIDER_MAX_CONCURRENCY"
    )

    # ==================== HTTP Client Timeouts ====================
    http_read_timeout: float = Field(
        default=300.0, validation_alias="HTTP_READ_TIMEOUT"
    )
    http_write_timeout: float = Field(
        default=10.0, validation_alias="HTTP_WRITE_TIMEOUT"
    )
    http_connect_timeout: float = Field(
        default=2.0, validation_alias="HTTP_CONNECT_TIMEOUT"
    )

    # ==================== Fast Prefix Detection ====================
    fast_prefix_detection: bool = True

    # ==================== Optimizations ====================
    enable_network_probe_mock: bool = True
    enable_title_generation_skip: bool = True
    enable_suggestion_mode_skip: bool = True
    enable_filepath_extraction_mock: bool = True
    enable_models_list_mock: bool = True

    # ==================== NIM Settings ====================
    nim: NimSettings = Field(default_factory=NimSettings)

    # ==================== Voice Note Transcription ====================
    voice_note_enabled: bool = Field(
        default=True, validation_alias="VOICE_NOTE_ENABLED"
    )
    # Device: "cpu" | "cuda" | "nvidia_nim"
    # - "cpu"/"cuda": local Whisper (requires voice_local extra: uv sync --extra voice_local)
    # - "nvidia_nim": NVIDIA NIM Whisper API (requires voice extra: uv sync --extra voice)
    whisper_device: str = Field(default="cpu", validation_alias="WHISPER_DEVICE")
    # Whisper model ID or short name (for local Whisper) or NVIDIA NIM model (for nvidia_nim)
    # Local Whisper: "tiny", "base", "small", "medium", "large-v2", "large-v3", "large-v3-turbo"
    # NVIDIA NIM: "nvidia/parakeet-ctc-1.1b-asr", "openai/whisper-large-v3", etc.
    whisper_model: str = Field(default="base", validation_alias="WHISPER_MODEL")
    # Hugging Face token for faster model downloads (optional, for local Whisper)
    hf_token: str = Field(default="", validation_alias="HF_TOKEN")

    # ==================== Bot Wrapper Config ====================
    telegram_bot_token: str | None = None
    allowed_telegram_user_id: str | None = None
    discord_bot_token: str | None = Field(
        default=None, validation_alias="DISCORD_BOT_TOKEN"
    )
    allowed_discord_channels: str | None = Field(
        default=None, validation_alias="ALLOWED_DISCORD_CHANNELS"
    )
    claude_workspace: str = "./agent_workspace"
    allowed_dir: str = ""

    # ==================== Server ====================
    host: str = "0.0.0.0"
    port: int = 8082
    log_file: str = "server.log"

    # Handle empty strings for optional string fields
    @field_validator(
        "telegram_bot_token",
        "allowed_telegram_user_id",
        "discord_bot_token",
        "allowed_discord_channels",
        mode="before",
    )
    @classmethod
    def parse_optional_str(cls, v):
        if v == "":
            return None
        return v

    @field_validator("whisper_device")
    @classmethod
    def validate_whisper_device(cls, v: str) -> str:
        if v not in ("cpu", "cuda", "nvidia_nim"):
            raise ValueError(
                f"whisper_device must be 'cpu', 'cuda', or 'nvidia_nim', got {v!r}"
            )
        return v

    @field_validator(
        "model_fallbacks",
        "model_opus_fallbacks",
        "model_sonnet_fallbacks",
        "model_haiku_fallbacks",
        mode="before",
    )
    @classmethod
    def parse_model_fallbacks(cls, v) -> list[str]:
        if v is None or v == "":
            return []
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                if not isinstance(parsed, list):
                    raise ValueError("Model fallbacks JSON value must be a list")
                return [str(item).strip() for item in parsed if str(item).strip()]
            return [item.strip() for item in stripped.split(",") if item.strip()]
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        raise ValueError("Model fallbacks must be a comma-separated string or list")

    @staticmethod
    def _validate_model_format_value(v: str) -> str:
        valid_providers = ("nvidia_nim", "open_router", "lmstudio")
        if "/" not in v:
            raise ValueError(
                f"Model must be prefixed with provider type. "
                f"Valid providers: {', '.join(valid_providers)}. "
                f"Format: provider_type/model/name"
            )
        provider = v.split("/", 1)[0]
        if provider not in valid_providers:
            raise ValueError(
                f"Invalid provider: '{provider}'. "
                f"Supported: 'nvidia_nim', 'open_router', 'lmstudio'"
            )
        return v

    @field_validator("model", "model_opus", "model_sonnet", "model_haiku")
    @classmethod
    def validate_model_format(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return cls._validate_model_format_value(v)

    @field_validator(
        "model_fallbacks",
        "model_opus_fallbacks",
        "model_sonnet_fallbacks",
        "model_haiku_fallbacks",
    )
    @classmethod
    def validate_model_fallback_formats(cls, v: list[str]) -> list[str]:
        return [cls._validate_model_format_value(item) for item in v]

    @field_validator("auto_model_default")
    @classmethod
    def validate_auto_model_default(cls, v: str) -> ModelTier:
        if v not in ("haiku", "sonnet", "opus"):
            raise ValueError("AUTO_MODEL_DEFAULT must be 'haiku', 'sonnet', or 'opus'")
        return cast(ModelTier, v)

    @model_validator(mode="after")
    def check_nvidia_nim_api_key(self) -> Settings:
        if (
            self.voice_note_enabled
            and self.whisper_device == "nvidia_nim"
            and not self.nvidia_nim_api_key.strip()
        ):
            raise ValueError(
                "NVIDIA_NIM_API_KEY is required when WHISPER_DEVICE is 'nvidia_nim'. "
                "Set it in your .env file."
            )
        return self

    @property
    def provider_type(self) -> str:
        """Extract provider type from the default model string."""
        return self.model.split("/", 1)[0]

    @property
    def model_name(self) -> str:
        """Extract the actual model name from the default model string."""
        return self.model.split("/", 1)[1]

    def resolve_model(self, claude_model_name: str) -> str:
        """Resolve a Claude model name to the configured provider/model string.

        Classifies the incoming Claude model (opus/sonnet/haiku) and
        returns the model-specific override if configured, otherwise the fallback MODEL.
        """
        name_lower = claude_model_name.lower()
        if "opus" in name_lower and self.model_opus is not None:
            return self.model_opus
        if "haiku" in name_lower and self.model_haiku is not None:
            return self.model_haiku
        if "sonnet" in name_lower and self.model_sonnet is not None:
            return self.model_sonnet
        return self.model

    def resolve_model_tier(self, tier: ModelTier) -> str:
        """Resolve a Claude model tier to a configured provider/model string."""
        if tier == "opus" and self.model_opus is not None:
            return self.model_opus
        if tier == "haiku" and self.model_haiku is not None:
            return self.model_haiku
        if tier == "sonnet" and self.model_sonnet is not None:
            return self.model_sonnet
        return self.model

    def _fallbacks_for_tier(self, tier: ModelTier) -> list[str]:
        if tier == "opus":
            return self.model_opus_fallbacks
        if tier == "haiku":
            return self.model_haiku_fallbacks
        return self.model_sonnet_fallbacks

    @staticmethod
    def _dedupe_models(models: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for model in models:
            if model in seen:
                continue
            seen.add(model)
            deduped.append(model)
        return deduped

    def resolve_model_tier_candidates(self, tier: ModelTier) -> list[str]:
        """Resolve a tier to primary model plus configured fallback candidates."""
        return self._dedupe_models(
            [
                self.resolve_model_tier(tier),
                *self._fallbacks_for_tier(tier),
                *self.model_fallbacks,
                self.model,
            ]
        )

    def resolve_request_model(
        self,
        claude_model_name: str,
        *,
        messages: list[object] | None = None,
        system_prompt: Any = None,
        tool_count: int = 0,
    ) -> tuple[str, ModelRoutingDecision | None]:
        """Resolve a request to provider/model, optionally using auto routing."""
        if not self.auto_model_enabled:
            return self.resolve_model(claude_model_name), None

        decision = route_model_tier(
            requested_model=claude_model_name,
            messages=messages,
            system_prompt=system_prompt,
            tool_count=tool_count,
            auto_default=self.auto_model_default,
            allow_opus=self.auto_model_allow_opus,
        )
        return self.resolve_model_tier(decision.tier), decision

    def resolve_request_model_candidates(
        self,
        claude_model_name: str,
        *,
        messages: list[object] | None = None,
        system_prompt: Any = None,
        tool_count: int = 0,
    ) -> tuple[list[str], ModelRoutingDecision | None]:
        """Resolve a request to ordered provider/model candidates."""
        if not self.auto_model_enabled:
            primary = self.resolve_model(claude_model_name)
            return (
                self._dedupe_models([primary, *self.model_fallbacks, self.model]),
                None,
            )

        decision = route_model_tier(
            requested_model=claude_model_name,
            messages=messages,
            system_prompt=system_prompt,
            tool_count=tool_count,
            auto_default=self.auto_model_default,
            allow_opus=self.auto_model_allow_opus,
        )
        return self.resolve_model_tier_candidates(decision.tier), decision

    @staticmethod
    def parse_provider_type(model_string: str) -> str:
        """Extract provider type from any 'provider/model' string."""
        return model_string.split("/", 1)[0]

    @staticmethod
    def parse_model_name(model_string: str) -> str:
        """Extract model name from any 'provider/model' string."""
        return model_string.split("/", 1)[1]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
