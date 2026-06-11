# claude-free fork notes

This repository is our maintained fork of `Rishurajgautam24/free-claude-code`,
adapted for WSL, Claude Code in VSCode, and NVIDIA NIM.

## Difference from upstream

Compared with the upstream `Rishurajgautam24/free-claude-code` project, this
fork keeps the same Anthropic-compatible proxy architecture but changes the
operational contract for Claude Code and VSCode.

- The upstream project is a generic free Claude Code proxy with provider
  mapping.
- This fork is tuned for WSL, the Claude Code VSCode extension, and NVIDIA NIM.
- This fork can resolve `--model auto` or missing model requests through a
  deterministic Claude-tier router.
- This fork maps Claude tiers to curated NVIDIA NIM models instead of relying
  only on a single fallback model.
- This fork logs the selected tier, route reason, and resolved provider model
  for each routed request.
- This fork adapts Anthropic-style `system` messages for OpenAI-compatible NIM
  backends by folding system content into the first user turn.
- This fork includes tests for auto-routing behavior, manual prompt overrides,
  NVIDIA NIM message adaptation, and Opus gating.

The main fork-specific files and edits are:

- `config/model_router.py`: deterministic prompt/router logic for `haiku`,
  `sonnet`, and `opus`.
- `config/settings.py`: auto-model settings and request-model resolution.
- `api/models/anthropic.py`: request routing, model metadata, prompt override
  stripping, and `AUTO_MODEL_ROUTE` logging.
- `providers/nvidia_nim/request.py`: Claude Code compatible message conversion
  for NVIDIA NIM.
- `providers/logging_utils.py`: compact route metadata in request logs.
- `tests/api/test_models_validators.py`: auto-router and override coverage.
- `tests/providers/test_nvidia_nim.py`: NVIDIA NIM compatibility coverage.
- `nvidia_nim_models.json`: curated NVIDIA NIM model inventory used for this
  fork's model selection.

## Current routing contract

The proxy is intended to run with `AUTO_MODEL_ENABLED=true`.

- Simple prompts route to `haiku`.
- Coding/tool prompts route to `sonnet`.
- Deep review, debugging, architecture, concurrency, security, migration, and
  large-context prompts route to `opus` when enabled.
- Manual prompt override is supported with `#model: haiku`, `#model: sonnet`, or
  `#model: opus`.
- The proxy strips manual `#model:` directives before forwarding to the provider.

## Current NVIDIA NIM mapping

- `MODEL_HAIKU`: `nvidia_nim/openai/gpt-oss-20b`
- `MODEL_SONNET`: `nvidia_nim/qwen/qwen3-next-80b-a3b-instruct`
- `MODEL_OPUS`: `nvidia_nim/nvidia/nemotron-3-super-120b-a12b`

## Operational notes

- Do not commit `.env`, logs, virtual environments, or local agent workspaces.
- Use `.env.example` as the public configuration template.
- The systemd user service in this workstation is named `freecc.service`.
- Claude Code/VSCode should point at `ANTHROPIC_BASE_URL=http://localhost:8082`.
- Requests log a safe `AUTO_MODEL_ROUTE` line with the requested model, selected
  tier, route reason, and resolved provider model.
