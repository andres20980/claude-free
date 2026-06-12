"""Pydantic models for Anthropic-compatible requests."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel, field_validator, model_validator

from config.model_router import strip_model_override
from config.settings import Settings, get_settings


# =============================================================================
# Content Block Types
# =============================================================================
class Role(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ContentBlockText(BaseModel):
    type: Literal["text"]
    text: str


class ContentBlockImage(BaseModel):
    type: Literal["image"]
    source: dict[str, Any]


class ContentBlockToolUse(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: str
    input: dict[str, Any]


class ContentBlockToolResult(BaseModel):
    type: Literal["tool_result"]
    tool_use_id: str
    content: str | list[Any] | dict[str, Any]


class ContentBlockThinking(BaseModel):
    type: Literal["thinking"]
    thinking: str


class SystemContent(BaseModel):
    type: Literal["text"]
    text: str


# =============================================================================
# Message Types
# =============================================================================
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: (
        str
        | list[
            ContentBlockText
            | ContentBlockImage
            | ContentBlockToolUse
            | ContentBlockToolResult
            | ContentBlockThinking
        ]
    )
    reasoning_content: str | None = None


class Tool(BaseModel):
    name: str
    description: str | None = None
    input_schema: dict[str, Any]


class ThinkingConfig(BaseModel):
    enabled: bool = True


# =============================================================================
# Request Models
# =============================================================================
class MessagesRequest(BaseModel):
    model: str
    max_tokens: int | None = None
    messages: list[Message]
    system: str | list[SystemContent] | None = None
    stop_sequences: list[str] | None = None
    stream: bool | None = True
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    metadata: dict[str, Any] | None = None
    tools: list[Tool] | None = None
    tool_choice: dict[str, Any] | None = None
    thinking: ThinkingConfig | None = None
    extra_body: dict[str, Any] | None = None
    original_model: str | None = None
    resolved_provider_model: str | None = None
    resolved_provider_model_candidates: list[str] = []
    provider_model_candidates: list[str] = []
    auto_model_tier: str | None = None
    auto_model_reason: str | None = None

    def _strip_manual_model_override(self) -> None:
        """Remove proxy-local #model directives before provider forwarding."""
        for message in reversed(self.messages):
            if message.role != "user":
                continue
            if isinstance(message.content, str):
                message.content = strip_model_override(message.content)
                return
            for block in message.content:
                if isinstance(block, ContentBlockText):
                    block.text = strip_model_override(block.text)
                    return

    @model_validator(mode="after")
    def map_model(self) -> MessagesRequest:
        """Map any Claude model name to the configured model (model-aware)."""
        settings = get_settings()
        if self.original_model is None:
            self.original_model = self.model

        candidates, routing = settings.resolve_request_model_candidates(
            self.original_model,
            messages=list(self.messages),
            tool_count=len(self.tools) if self.tools else 0,
        )
        resolved_full = candidates[0]
        if routing is not None:
            self.auto_model_tier = routing.tier
            self.auto_model_reason = routing.reason
            logger.info(
                "AUTO_MODEL_ROUTE: "
                f"requested='{self.original_model}' "
                f"tier='{routing.tier}' "
                f"reason='{routing.reason}' "
                f"resolved='{resolved_full}'"
            )
            if routing.override_used and settings.auto_model_strip_override:
                self._strip_manual_model_override()

        self.resolved_provider_model = resolved_full
        self.resolved_provider_model_candidates = candidates
        primary_provider = Settings.parse_provider_type(resolved_full)
        self.provider_model_candidates = [
            Settings.parse_model_name(candidate)
            for candidate in candidates
            if Settings.parse_provider_type(candidate) == primary_provider
        ]
        self.model = Settings.parse_model_name(resolved_full)

        if self.model != self.original_model:
            logger.debug(f"MODEL MAPPING: '{self.original_model}' -> '{self.model}'")

        return self


class TokenCountRequest(BaseModel):
    model: str
    messages: list[Message]
    system: str | list[SystemContent] | None = None
    tools: list[Tool] | None = None
    thinking: ThinkingConfig | None = None
    tool_choice: dict[str, Any] | None = None

    @field_validator("model")
    @classmethod
    def validate_model_field(cls, v: str, info) -> str:
        """Map any Claude model name to the configured model (model-aware)."""
        settings = get_settings()
        resolved_full, _ = settings.resolve_request_model(v)
        return Settings.parse_model_name(resolved_full)
