---
id: ADR-005
title: OpenAI Client für LLM-Provider-Konfigurierbarkeit (FR-D-12)
status: Accepted
date: 2026-03-13
---

# ADR-005: OpenAI Client — openai SDK als neue Abhängigkeit

## Context

FR-D-12 fordert LLM-Provider-Konfigurierbarkeit ohne Code-Änderung. Der erste
Nutzer des Systems hat nur einen OpenAI API-Key, nicht Anthropic. Der OllamaClient
ist ein nicht-funktionaler Stub. Um das System testbar zu machen, wird ein
vollständiger OpenAIClient benötigt.

Das `openai` Python-SDK ist noch nicht in requirements.txt.

## Decision

`openai>=1.0.0` wird zu requirements.txt hinzugefügt.
`backend/llm/openai_client.py` implementiert `OpenAIClient(LLMClient)`.
Die Factory unterstützt `LLM_PROVIDER=openai`.

## Rationale

- Die `LLMClient`-Abstraktion wurde explizit für Provider-Austauschbarkeit entworfen
- OpenAI Function Calling ist semantisch identisch mit Anthropic Tool Use
- Der `openai`-SDK ist battle-tested und stabil (v1.x)
- Kein Architektur-Eingriff: neues File im bestehenden `backend/llm/`-Verzeichnis

## Format-Übersetzung

Anthropic Tool Use → OpenAI Function Calling:

| Anthropic             | OpenAI                          |
|-----------------------|---------------------------------|
| `input_schema`        | `parameters` (in `function`)    |
| `content[].type == "tool_use"` | `choices[0].message.tool_calls` |
| `tool_use.input`      | `tool_calls[0].function.arguments` (JSON string) |
| `usage.input_tokens`  | `usage.prompt_tokens`           |
| `usage.output_tokens` | `usage.completion_tokens`       |

## Consequences

- `openai` wird als Pflichtabhängigkeit hinzugefügt (auch wenn Provider=anthropic)
- Alternativ: optional import mit try/except — aber das erhöht Komplexität unnötig
- OpenAI-Modelle unterstützen Function Calling ab `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
