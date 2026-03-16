# EMMA Parameter Extraction Prompt

## Instructions for use

Copy everything from the **"PROMPT START"** heading below and paste it into Claude Code,
followed by the full content of the EMMA automation tool handbook. The handbook text should
immediately follow the prompt without any separator.

---

## PROMPT START

You are helping to build a typed Python backend for an EMMA automation system. I will give
you the full EMMA handbook text after this prompt. Please extract the parameter specification
for every action type as described below.

### Background

We have a Pydantic v2 data model `EmmaAktion` in Python:

```python
class EmmaAktion(BaseModel):
    aktion_id: str
    aktionstyp: EmmaAktionstyp      # one of the 18 enum values listed below
    parameter: dict[str, str]       # PLACEHOLDER — this is what we are replacing
    nachfolger: list[str]           # successor action IDs; ["END"] marks termination
    emma_kompatibel: bool = False
    kompatibilitaets_hinweis: str | None = None
```

The `EmmaAktionstyp` enum currently contains these 18 values:

```
FIND, FIND_AND_CLICK, CLICK, DRAG, SCROLL, TYPE, READ, READ_FORM,
GENAI, EXPORT, IMPORT, FILE_OPERATION, SEND_MAIL, COMMAND,
LOOP, DECISION, WAIT, SUCCESS
```

**Important:** If the handbook documents additional action types not in this list, extract
them too and include them in the output. They must be added to the enum and receive their
own parameter model. Flag each new type explicitly with `[NEW — not yet in enum]`.

The goal is to replace `parameter: dict[str, str]` with a **discriminated union of
per-action-type Pydantic models**, one model class per action type. For example:

```python
class FindParameter(BaseModel):
    target: str                         # required — what to locate
    search_region: str | None = None    # optional — bounding region hint

class ClickParameter(BaseModel):
    target: str
    button: Literal["left", "right", "double"] = "left"

# ... one model per action type ...

EmmaAktionParameter = Annotated[
    FindParameter | FindAndClickParameter | ClickParameter | ...,
    Field(discriminator="aktionstyp")   # or a wrapper union without discriminator
]
```

An LLM generates `EmmaAktion` objects at runtime, so the models must be:
- Precise enough to validate what the LLM produces
- Flexible enough that optional/unknown parameters do not hard-fail validation

---

### What to extract from the handbook

For **every action type found in the handbook** — including the 18 listed above and any
additional types the handbook documents — produce one section in the output (see output
format below). Within each section answer all of the following questions from the handbook
text:

1. **Required parameters** — name, Python type, description, any constraints
2. **Optional parameters** — name, Python type, default value (if given), description,
   any constraints
3. **Enum / literal values** — wherever the handbook restricts a parameter to a fixed
   set of values, list every allowed value exactly as written
4. **Numeric / string constraints** — ranges, regex patterns, max lengths, formats
5. **Inter-parameter dependencies** — conditions where one parameter is only valid
   when another parameter has a specific value
6. **A minimal valid example** — the smallest parameter set that produces a valid action
   of this type (JSON object notation)

Additionally, answer the following **cross-cutting questions** in a dedicated section at
the end:

**A. `nachfolger` semantics**
- What does `nachfolger: list[str]` represent generally?
- Is the value always an `aktion_id` from the same `Algorithmusabschnitt`, or can it
  reference actions in other sections?
- What sentinel value signals "no further action / end of flow"? (We currently use
  `["END"]` — confirm or correct this.)
- For a normal linear action, how many elements does `nachfolger` typically have?

**B. DECISION branching**
- How many successors does a DECISION action have?
- How are the branches distinguished — by index, by label, by a parameter key?
- What parameter(s) encode the branching condition (e.g. a boolean expression,
  a comparison, an enum value)?
- Is there a default/else branch? If so, how is it marked?
- Provide an example DECISION action in full (aktionstyp, parameter dict, nachfolger list).

**C. LOOP iteration**
- What does the LOOP action iterate over? (a list, a count, a file set, …)
- Which parameter specifies the collection / iteration variable?
- Which parameter (or nachfolger element) points to the first action inside the loop body?
- Which parameter (or nachfolger element) points to the action after the loop exits?
- How is the loop variable referenced inside the loop body actions?
- Provide an example LOOP action in full (aktionstyp, parameter dict, nachfolger list).

**D. SUCCESS / termination semantics**
- Does SUCCESS take any parameters?
- Can there be multiple SUCCESS actions in one algorithm section?
- Does SUCCESS always appear as a leaf node (empty nachfolger / `["END"]`)?
- Is there a FAILURE or ERROR terminal action type, or is failure handled differently?

**E. Action-type-specific validation rules**
- Are there any action types that are only valid in certain contexts (e.g. only inside
  a LOOP body, only as the first action)?
- Are there parameter combinations that are explicitly forbidden?
- Are there parameter combinations that the handbook warns are error-prone?

---

### Output format

Produce output in the following structured Markdown. Do not omit any action type even if
the handbook provides minimal information — in that case state "Not specified in handbook"
for each sub-field. Mark action types not yet in the enum with `[NEW — not yet in enum]`
in the heading.

```
## Action Type: <AKTIONSTYP>

**Purpose:** <one-sentence description from handbook>

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| name      | str         | max 255 chars | … |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| name      | str \| None | None   | …           | … |

### Enum Values

If any parameter is restricted to a fixed set of values:

- `parameter_name`: `"value_a"` | `"value_b"` | `"value_c"`

### Constraints & Validation Rules

- <bullet per rule>

### Minimal Valid Example

```json
{
  "aktionstyp": "AKTIONSTYP",
  "parameter": {
    "key": "value"
  },
  "nachfolger": ["<next_aktion_id>"]
}
```

### Pydantic Model Skeleton (fill in from above)

```python
class AktionstypenameParameter(BaseModel):
    required_field: str
    optional_field: str | None = None
```
```

After all action-type sections, append the cross-cutting sections A through E using
the same heading level (`## A. nachfolger semantics`, etc.).

---

### Final deliverable

After the extraction, produce one additional section:

## Suggested Pydantic Union

Write a Python code block showing the complete union type that would replace
`parameter: dict[str, str]` in `EmmaAktion`. Include:

1. All parameter model classes — one per action type found in the handbook (bodies may
   be `...` / `pass` as placeholders where the handbook gives insufficient detail)
2. An updated `EmmaAktionstyp` StrEnum that includes both the original 18 values and any
   new types found in the handbook (new values marked with `# NEW` comment)
3. A `EmmaAktionParameter` union type using `typing.Union` or the `|` operator
4. Any `Literal` or `StrEnum` types needed for enum parameters
5. Import statements (`from __future__ import annotations`, `from pydantic import …`,
   `from typing import …`, etc.)
6. A note for each model class that had to use placeholders, explaining what is still
   missing from the handbook

The code does not need to be runnable as-is. It should be precise enough that a developer
can fill in the blanks and have a working Pydantic v2 discriminated union.

## PROMPT END
