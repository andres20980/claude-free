# claude-free fork notes

This repository is our maintained fork of `Rishurajgautam24/free-claude-code`,
adapted for WSL, Claude Code in VSCode, and NVIDIA NIM.

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
