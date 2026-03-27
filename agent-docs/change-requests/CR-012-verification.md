# Verifikation: CR-012 — Strukturgraph Bidirektionale Verifikation

| Feld | Wert |
|---|---|
| **CR** | CR-012 |
| **Verifikationsdatum** | 2026-03-27 |
| **Ergebnis** | BESTANDEN |

## Zusammenfassung

CR-012 wurde durch 5 unabhängige Verifikations-Prüfungen analysiert (Änderungsplan-Vollständigkeit, Abnahmekriterien, Tests, Mitigationen/Bedingungen, SDD/ADR-Konformität). Alle 10 Plan-Zeilen sind umgesetzt, alle 8 Abnahmekriterien erfüllt, alle 5 Review-Bedingungen eingehalten, und die Implementierung ist SDD- und ADR-konform.

## Ergebnis

**BESTANDEN**

Die Implementierung ist vollständig, korrekt und abwärtskompatibel. Keine Blocker, keine Lücken. Abweichungen vom Plan sind durch Review-Bedingungen begründet und sinnvoll.

## Änderungsplan-Vollständigkeit

| # | Plan-Zeile | Status | Details |
|---|---|---|---|
| 1 | models.py: vorgaenger-Feld | Umgesetzt | `models.py:153` — `vorgaenger: list[str] = Field(default_factory=list)` |
| 2 | template_schema.py: Patch-Pfad | Umgesetzt | `template_schema.py:111-114` — Pattern mit `["replace"]` |
| 3 | init_validator.py: Konsistenzregel | Umgesetzt | `init_validator.py:54-74` — R-1 Referenzprüfung + R-2 bidirektionale Konsistenz |
| 4 | executor.py: nicht-invalidierend | Abweichend | Review-Bedingung 5: Invalidierung automatisch korrekt. Stattdessen: `_derive_vorgaenger` Guardrail (Review-Bedingung 1) |
| 5 | init_structuring.md: Prompt | Abweichend | Review-Bedingung 3: Nur Schema-Tabelle (Zeile 245), keine Patch-Beispiele (Guardrail macht LLM-Pflege überflüssig) |
| 6 | structuring.md: Prompt | Abweichend | Review-Bedingung 3: Nur Schema-Tabelle (Zeile 197), keine Patch-Beispiele |
| 7 | test_artifact_models.py: Tests | Umgesetzt | 2 neue Tests: `test_vorgaenger_defaults_to_empty_list`, `test_vorgaenger_roundtrip` |
| 8 | test_init_validator.py: Tests | Umgesetzt | 5 neue Tests: R-1 vorgaenger-Referenz + R-2 bidirektionale Konsistenz (4 Szenarien) |
| 9 | test_executor.py: Tests | Umgesetzt | 5 neue Tests: Patch-Pfad (2), Nicht-Invalidierung (1), Guardrail-Ableitung (2) |
| 10 | SDD: Dokumentation | Umgesetzt | Zeile 700: "Anzeigereihenfolge", Zeile 702: vorgaenger, Zeilen 817-818: Invariante, Zeile 821: Invalidierungsregel |

## Abnahmekriterien

| # | Kriterium | Erfüllt? | Evidenz |
|---|---|---|---|
| 1 | `vorgaenger: list[str]` mit Default `[]` | Ja | `models.py:153` |
| 2 | Template erlaubt `replace` auf vorgaenger | Ja | `template_schema.py:111-114` |
| 3 | Keine Algorithmus-Invalidierung | Ja | `executor.py:53` — nicht in `_INVALIDATING_FIELDS` |
| 4 | Validator meldet Inkonsistenzen als `kritisch` | Ja | `init_validator.py:68-74` |
| 5 | Bestehende Tests grün | Ja | 469/471, 2 vorbestehende Fehler (nicht CR-012) |
| 6 | Neue Tests vorhanden | Ja | 12 neue Tests in 3 Dateien |
| 7 | Prompts dokumentieren vorgaenger | Ja | init_structuring.md:245, structuring.md:197 |
| 8 | SDD aktualisiert | Ja | SDD:700, 702, 817-821 |

## Test-Ergebnisse

- **CR-012-relevante Tests**: 105/105 bestanden (test_artifact_models, test_init_validator, test_executor)
- **Gesamte Suite**: 469/471 bestanden, 2 fehlgeschlagen
- **Fehlgeschlagene Tests**: `test_specification_system_prompt_contains_emma_catalog` und `test_specification_system_prompt_contains_operationalisierbarkeit` — vorbestehende Fehler durch Änderungen an specification.py/specification.md, die bereits vor CR-012 im Working Tree waren. Nicht CR-012-bedingt.
- **Abwärtskompatibilität**: Bestanden — ca. 30 bestehende `Strukturschritt()`-Aufrufe ohne vorgaenger funktionieren dank Default `[]`
- **Test-Gaps**: Keine im CR-012-Scope

## Mitigationen & Review-Bedingungen

| # | Mitigation/Bedingung | Umgesetzt? | Evidenz |
|---|---|---|---|
| M1 | Guardrail statt LLM-Pflege | Ja | `executor.py:37-49` — `_derive_vorgaenger()` nach jedem Patch-Cycle |
| M2 | Default [] für alte Artefakte | Ja | `models.py:153` — `Field(default_factory=list)` |
| M3 | vorgaenger nicht in Prompt-Beispielen | Ja | Prompts: nur Schema-Tabelle, keine Patch-Beispiele |
| RC-1 | Code-Guardrail als Pflicht | Ja | `executor.py:176-179` — Step 6a in Pipeline |
| RC-2 | reihenfolge in Prompts unverändert | Ja | Prompts bereits korrekt, keine Änderung nötig |
| RC-3 | Prompt-Änderungen minimiert | Ja | Nur 1 Zeile Schema-Tabelle je Prompt |
| RC-4 | Validator: alte Artefakte korrekt | Ja | `init_validator.py:59-74` — vergleicht ist vs. erwartet |
| RC-5 | Executor: keine Invalidierungsänderung | Ja | `_INVALIDATING_FIELDS` unverändert |

## SDD- & ADR-Konformität

**SDD-Konformität**: Vollständig konform. `reihenfolge`-Semantik korrigiert, `vorgaenger`-Feld dokumentiert, bidirektionale Invariante definiert, Invalidierungsregel aktualisiert. Keine SDD-Prinzipien verletzt (LLM als Operator — vorgaenger wird vom System abgeleitet, nicht vom LLM; deterministische Orchestrierung — Executor-Guardrail ist deterministisch).

| ADR-Aspekt | Konform? | Evidenz |
|---|---|---|
| Neues Feld vorgaenger als inverse Referenz | Ja | `models.py:153` |
| O(n)-Konsistenzprüfung statt O(n²)-Traversierung | Ja | `init_validator.py:59-74` |
| SDD-Update durchgeführt | Ja | SDD:700, 702, 817-821 |
| Template-Schema erweitert | Ja | `template_schema.py:111-114` |
| Prompts aktualisiert | Ja | Schema-Tabelle in beiden Prompts |

## Blocker (müssen nachgebessert werden)

Keine.

## Abweichungen vom Plan

1. **Plan-Zeile 4 (executor.py)**: Statt vorgaenger zu nicht-invalidierenden Feldern hinzuzufügen (unnötig, da automatisch nicht-invalidierend), wurde der Code-Guardrail `_derive_vorgaenger` implementiert (Review-Bedingung 1). Sinnvolle Abweichung.
2. **Plan-Zeilen 5+6 (Prompts)**: Statt vorgaenger in alle Patch-Beispiele aufzunehmen, nur Schema-Tabelle ergänzt (Review-Bedingung 3, Guardrail macht LLM-Pflege überflüssig). Sinnvolle Abweichung.

## Lücken

Keine.
