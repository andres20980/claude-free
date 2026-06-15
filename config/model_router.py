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
        # Spanish
        "arquitectura",
        "concurrencia",
        "deadlock",
        "difícil",
        "dificil",
        "fallo",
        "incidente",
        "migración",
        "migracion",
        "regresión",
        "regresion",
        "revisión",
        "revision",
        "seguridad",
        "vulnerabilidad",
        "optimizar",
        "optimización",
        "optimizacion",
        "complejo",
        "complejidad",
        "análisis",
        "analisis",
        "auditoría",
        "auditoria",
        "cuello de botella",
        "fuga de memoria",
        "cifrado",
        "algoritmo",
        "diseño",
        "diseno",
        # English
        "architecture",
        "auditor",
        "concurrency",
        "deep_review",
        "debug",
        "debugging",
        "error",
        "failing",
        "fails",
        "flaky",
        "migration",
        "perf",
        "performance",
        "race",
        "refactor",
        "review",
        "security",
        "optimize",
        "optimization",
        "complex",
        "complexity",
        "analysis",
        "audit",
        "bottleneck",
        "memory leak",
        "leak",
        "encryption",
        "cryptography",
        "algorithm",
        "design",
        "refactoring",
        "thread",
        "multithreading",
        "async",
        "asynchronous",
        "race condition",
        "lock",
        "mutex",
    }
)

_CODE_KEYWORDS = frozenset(
    {
        # Spanish
        "código",
        "codigo",
        "editar",
        "función",
        "funcion",
        "implementar",
        "prueba",
        "programa",
        "programación",
        "programacion",
        "clase",
        "método",
        "metodo",
        "variable",
        "importar",
        "librería",
        "libreria",
        "biblioteca",
        "módulo",
        "modulo",
        "archivo",
        "fichero",
        "línea",
        "linea",
        "compilar",
        "ejecutar",
        "consola",
        "terminal",
        "desplegar",
        "repositorio",
        "rama",
        "base de datos",
        "consulta",
        "servidor",
        "cliente",
        "interfaz",
        "componente",
        # English
        "api",
        "bug",
        "code",
        "commit",
        "diff",
        "extension",
        "fix",
        "implement",
        "patch",
        "pytest",
        "script",
        "test",
        "vscode",
        "wsl",
        "program",
        "programming",
        "class",
        "method",
        "import",
        "library",
        "module",
        "file",
        "line",
        "compile",
        "run",
        "deploy",
        "deployment",
        "git",
        "repo",
        "repository",
        "branch",
        "merge",
        "pr",
        "pull request",
        "database",
        "db",
        "query",
        "server",
        "client",
        "interface",
        "ui",
        "component",
        "endpoint",
        "json",
        "yaml",
        "xml",
        "html",
        "css",
        "js",
        "ts",
        "python",
        "rust",
        "go",
        "cpp",
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


def extract_text_from_messages(
    messages: list[Any] | None,
    system_prompt: str | list[Any] | None = None,
) -> str:
    """Extract concatenated text from messages and system prompt without provider dependencies."""
    parts: list[str] = []

    # Process system prompt first
    if system_prompt:
        if isinstance(system_prompt, str):
            parts.append(system_prompt)
        elif isinstance(system_prompt, list):
            for block in system_prompt:
                text = getattr(block, "text", "")
                if isinstance(text, str) and text:
                    parts.append(text)
                elif isinstance(block, dict) and "text" in block:
                    parts.append(block["text"])

    if messages:
        for message in messages:
            role = getattr(message, "role", None)
            if role not in ("user", "assistant", "system"):
                continue
            content = getattr(message, "content", "")
            if isinstance(content, str):
                if "<system-reminder>" not in content:
                    parts.append(content)
                continue
            if isinstance(content, list):
                for block in content:
                    text = getattr(block, "text", "")
                    if isinstance(text, str) and text:
                        if "<system-reminder>" not in text:
                            parts.append(text)
                    elif isinstance(block, dict) and "text" in block:
                        text_val = block["text"]
                        if (
                            isinstance(text_val, str)
                            and "<system-reminder>" not in text_val
                        ):
                            parts.append(text_val)
                    elif role == "user" and getattr(block, "type", "") == "tool_result":
                        tool_content = getattr(block, "content", "")
                        if isinstance(tool_content, str):
                            if "<system-reminder>" not in tool_content:
                                parts.append(tool_content)
                        elif isinstance(tool_content, list):
                            for sub_block in tool_content:
                                text_val = getattr(sub_block, "text", "")
                                if isinstance(text_val, str) and text_val:
                                    if "<system-reminder>" not in text_val:
                                        parts.append(text_val)
                                elif (
                                    isinstance(sub_block, dict) and "text" in sub_block
                                ):
                                    sub_text = sub_block["text"]
                                    if (
                                        isinstance(sub_text, str)
                                        and "<system-reminder>" not in sub_text
                                    ):
                                        parts.append(sub_text)

    return "\n".join(parts)


def extract_current_query(
    messages: list[Any] | None,
    system_prompt: str | list[Any] | None = None,
) -> str:
    """Extract only the active/current user query text to analyze for tier selection."""
    parts: list[str] = []

    # Process system prompt first if it is short
    if system_prompt:
        system_text = extract_text_from_messages(None, system_prompt)
        system_words = re.findall(r"\w+", system_text.lower())
        if len(system_words) <= 150:
            parts.append(system_text)

    if messages:
        # Find the last message with role == "user"
        for message in reversed(messages):
            role = getattr(message, "role", None)
            if role is None and isinstance(message, dict):
                role = message.get("role")

            if role == "user":
                content = getattr(message, "content", None)
                if content is None and isinstance(message, dict):
                    content = message.get("content")

                if isinstance(content, str):
                    if "<system-reminder>" not in content:
                        parts.append(content)
                elif isinstance(content, list):
                    for block in content:
                        block_type = getattr(block, "type", "")
                        if block_type == "" and isinstance(block, dict):
                            block_type = block.get("type", "")

                        # Exclude tool_result content from the active user query complexity classification,
                        # because past tool results (like huge file reads or output errors) should not escalate
                        # subsequent simple user queries to expensive tiers.
                        if block_type == "tool_result":
                            continue

                        text = getattr(block, "text", "")
                        if (text is None or text == "") and isinstance(block, dict):
                            text = block.get("text", "")
                        if (
                            isinstance(text, str)
                            and text
                            and ("<system-reminder>" not in text)
                        ):
                            parts.append(text)
                break

    return "\n".join(parts)


def route_model_tier(
    *,
    requested_model: str,
    messages: list[Any] | None,
    system_prompt: str | list[Any] | None = None,
    tool_count: int,
    auto_default: ModelTier,
    allow_opus: bool,
) -> ModelRoutingDecision:
    """Choose a Claude tier using deterministic local rules.

    Manual ``#model: tier`` overrides win. Otherwise, explicit Claude model
    names keep their tier unless the request looks simple enough for Haiku or
    complex enough for Opus.
    """
    system_text = (
        extract_text_from_messages(None, system_prompt) if system_prompt else ""
    )
    system_words = re.findall(r"\w+", system_text.lower())
    if len(system_words) <= 150:
        full_text = extract_text_from_messages(messages, system_prompt)
    else:
        full_text = extract_text_from_messages(messages, None)

    override = find_model_override(full_text)
    if override is not None:
        if override == "opus" and not allow_opus:
            return ModelRoutingDecision("sonnet", "manual_opus_disabled", True)
        return ModelRoutingDecision(override, "manual_override", True)

    explicit_tier = classify_claude_tier(requested_model)
    base_tier = explicit_tier or auto_default

    # We evaluate complexity and keywords based ONLY on the active user query
    # (and system prompt if it is short) to prevent past tool outputs or historical
    # error logs in the conversation from polluting the classification.
    active_query = extract_current_query(messages, system_prompt)
    normalized = active_query.lower()
    words = re.findall(r"\w+", normalized)
    word_count = len(words)
    has_code_marker = "```" in active_query or any(
        token in active_query for token in ("diff --git", "{", "};")
    )
    has_deep_signal = any(keyword in normalized for keyword in _DEEP_KEYWORDS)
    has_code_signal = any(keyword in normalized for keyword in _CODE_KEYWORDS)

    if allow_opus and (has_deep_signal or word_count > 1200):
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
