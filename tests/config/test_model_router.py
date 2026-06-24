from typing import Any

from config.model_router import route_model_tier


class DummyMessage:
    def __init__(self, role: str, content: Any):
        self.role = role
        self.content = content


def test_route_model_tier_simple_prompt():
    # Simple query with few words -> haiku
    decision = route_model_tier(
        requested_model="claude-sonnet-4-20250514",
        messages=[DummyMessage(role="user", content="capital of France")],
        tool_count=0,
        auto_default="sonnet",
        allow_opus=True,
    )
    assert decision.tier == "haiku"
    assert decision.reason == "short_simple_prompt"


def test_route_model_tier_word_boundary_capital():
    # Contains "capital" which has "api" substring, but API is word-bounded.
    # Should not trigger code signal and should route to haiku.
    decision = route_model_tier(
        requested_model="claude-sonnet-4-20250514",
        messages=[DummyMessage(role="user", content="cual es la capital de francia")],
        tool_count=0,
        auto_default="sonnet",
        allow_opus=True,
    )
    assert decision.tier == "haiku"
    assert decision.reason == "short_simple_prompt"


def test_route_model_tier_code_keyword():
    # Contains "función" which is a code keyword. Should trigger code signal -> sonnet.
    decision = route_model_tier(
        requested_model="claude-sonnet-4-20250514",
        messages=[DummyMessage(role="user", content="Escribe una función en Python")],
        tool_count=0,
        auto_default="sonnet",
        allow_opus=True,
    )
    assert decision.tier == "sonnet"
    assert decision.reason == "code_or_tool_signal"


def test_route_model_tier_tool_activity_persistence():
    # Simple active query, but messages list contains a tool result block.
    # Should bypass haiku routing -> sonnet.
    messages = [
        DummyMessage(role="user", content="Escribe una función"),
        DummyMessage(
            role="assistant",
            content=[
                {
                    "type": "tool_use",
                    "id": "1",
                    "name": "Bash",
                    "input": {"command": "ls"},
                }
            ],
        ),
        DummyMessage(
            role="user",
            content=[
                {"type": "tool_result", "tool_use_id": "1", "content": "file1.txt"}
            ],
        ),
    ]
    decision = route_model_tier(
        requested_model="claude-sonnet-4-20250514",
        messages=messages,
        tool_count=0,
        auto_default="sonnet",
        allow_opus=True,
    )
    assert decision.tier == "sonnet"
    assert decision.reason == "code_or_tool_signal"
