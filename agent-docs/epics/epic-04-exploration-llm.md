# Epic 04 – Exploration Mode & LLM Integration

## Summary

Replace the Exploration stub with a real `ExplorationMode` that calls the configured LLM
via the `LLMClient` abstraction. This epic also introduces the `ContextAssembler` (builds
the prompt from Working Memory) and `OutputValidator` (verifies the LLM's structured tool-use
output). After this epic a human can type a message and receive a genuine AI response that
begins populating the Exploration Artifact.

This epic corresponds to **Implementation Step 4** in `AGENTS.md` / `hla_architecture.md`.

## Goal

First end-to-end LLM turn: user message goes in, AI response comes back via the
Anthropic Tool Use API, the Exploration Artifact receives its first real content, and
everything is persisted.

## Testable Increment

- Running `pytest backend/tests/test_exploration_mode.py` with a live `ANTHROPIC_API_KEY`
  (or a recorded cassette / mock) → one full turn completes, artifact updated
- Alternatively: a small CLI test script (`python -m backend.scripts.test_turn`) sends a
  hard-coded user message and prints the AI reply + resulting artifact diff
- Observable without a frontend or WebSocket

## Dependencies

- Epic 03 (Orchestrator must be in place to wire the mode into the cycle)

## Key Deliverables

- `backend/llm/client.py` – `LLMClient` abstraction + `AnthropicClient` implementation
- `backend/llm/ollama_client.py` – `OllamaClient` stub (config-selectable, not required
  to be fully functional this epic)
- `backend/core/context_assembler.py` – `ContextAssembler`
- `backend/core/output_validator.py` – `OutputValidator`
- `backend/modes/exploration_mode.py` – `ExplorationMode` (real LLM calls)
- `backend/tests/test_exploration_mode.py` – integration test (mocked or live)
- `backend/.env.example` updated with `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`

## OpenAPI Contract Note

This epic introduces no new REST API endpoints. However, the streaming event payloads
(`chat_token`, `chat_done`, `artifact_update`, `error`) that the orchestrator will emit
via WebSocket should be defined as Pydantic models in this epic (e.g. in
`backend/api/schemas.py` or a shared `backend/core/events.py`). Typed event models allow
Epic 05 to reference them directly in the WebSocket endpoint schema without rework, and
keep the generated OpenAPI spec accurate.

## Stories

_To be defined before this epic begins._
