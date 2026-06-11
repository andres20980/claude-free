"""Local request router for automatic Claude-tier selection."""

import re
from dataclasses import dataclass
from typing import Any, Literal, cast

ModelTier = Literal["haiku", "sonnet", "opus"]

_MODEL_OVERRIDE_RE = re.compile(
    r"(?im)^[ \t]*#[ \t]*model[ \t]*:[ \t]*(haiku|sonnet|opus)[ \t]*$"
)

_DEEP_KEYWORDS = frozenset(
    {
        "arquitectura",
        "architecture",
        "auditor",
        "concurrencia",
        "concurrency",
        "deadlock",
        "deep_review",
        "debug",
        "debugging",
        "difícil",
        "dificil",
        "error",
        "failing",
        "fallo",
        "fails",
        "flaky",
        "incidente",
        "migration",
        "migración",
        "migracion",
        "perf",
        "performance",
        "race",
        "refactor",
        "regresión",
        "regresion",
        "review",
        "revisión",
        "revision",
        "security",
        "seguridad",
        "vulnerabilidad",
    }
)

_CODE_KEYWORDS = frozenset(
    {
        "api",
        "bug",
        "código",
        "codigo",
        "code",
        "commit",
        "diff",
        "editar",
        "extension",
        "fix",
        "función",
        "funcion",
        "implementar",
        "implement",
        "patch",
        "prueba",
        "pytest",
        "script",
        "test",
        "vscode",
        "wsl",
    }
)


@dataclass(frozen=True)
class ModelRoutingDecision:
    """Chosen Claude tier plus safe diagnostic metadata."""

    tier: ModelTier
    reason: str
    override_used: bool = False


def classify_claude_tier(model_name: str) -> ModelTier | None:
    """Classify an explicit Claude model name by tier."""
    name_lower = model_name.lower()
    if "opus" in name_lower:
        return "opus"
    if "haiku" in name_lower:
        return "haiku"
    if "sonnet" in name_lower:
        return "sonnet"
    return None


def find_model_override(text: str) -> ModelTier | None:
    """Return a manual #model override if present."""
    match = _MODEL_OVERRIDE_RE.search(text)
    if match is None:
        return None
    tier = match.group(1).lower()
    if tier in ("haiku", "sonnet", "opus"):
        return cast(ModelTier, tier)
    return None


def strip_model_override(text: str) -> str:
    """Remove manual #model override directives from prompt text."""
    return _MODEL_OVERRIDE_RE.sub("", text).strip()


def extract_text_from_messages(messages: list[Any] | None) -> str:
    """Extract concatenated text from user messages without provider dependencies."""
    if not messages:
        return ""

    parts: list[str] = []
    for message in messages:
        if getattr(message, "role", None) != "user":
            continue
        content = getattr(message, "content", "")
        if isinstance(content, str):
            parts.append(content)
            continue
        if isinstance(content, list):
            for block in content:
                text = getattr(block, "text", "")
                if isinstance(text, str) and text:
                    parts.append(text)
    return "\n".join(parts)


def route_model_tier(
    *,
    requested_model: str,
    messages: list[Any] | None,
    tool_count: int,
    auto_default: ModelTier,
    allow_opus: bool,
) -> ModelRoutingDecision:
    """Choose a Claude tier using deterministic local rules.

    Manual ``#model: tier`` overrides win. Otherwise, explicit Claude model
    names keep their tier unless the request looks simple enough for Haiku or
    complex enough for Opus.
    """
    text = extract_text_from_messages(messages)
    override = find_model_override(text)
    if override is not None:
        if override == "opus" and not allow_opus:
            return ModelRoutingDecision("sonnet", "manual_opus_disabled", True)
        return ModelRoutingDecision(override, "manual_override", True)

    explicit_tier = classify_claude_tier(requested_model)
    base_tier = explicit_tier or auto_default

    normalized = text.lower()
    words = re.findall(r"\w+", normalized)
    word_count = len(words)
    has_code_marker = "```" in text or any(
        token in text for token in ("diff --git", "{", "};")
    )
    has_deep_signal = any(keyword in normalized for keyword in _DEEP_KEYWORDS)
    has_code_signal = any(keyword in normalized for keyword in _CODE_KEYWORDS)

    if allow_opus and (has_deep_signal or word_count > 1200 or tool_count > 12):
        return ModelRoutingDecision("opus", "deep_signal")

    if (
        tool_count == 0
        and word_count <= 40
        and not has_code_marker
        and not has_code_signal
        and not has_deep_signal
    ):
        return ModelRoutingDecision("haiku", "short_simple_prompt")

    if has_code_signal or has_code_marker or tool_count > 0:
        return ModelRoutingDecision("sonnet", "code_or_tool_signal")

    return ModelRoutingDecision(base_tier, "default")
