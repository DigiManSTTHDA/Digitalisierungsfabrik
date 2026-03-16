# EMMA Studio 2.7 — Parameter Extraction Result

> Source: `docs/emma-studio-27-benutzerhandbuch.md`
> Extracted: 2026-03-16
> Model: Claude Sonnet 4.6

---

## Action Type: FIND

**Purpose:** Searches the screen, a file, or a previous step's result field for an object, text pattern, image, language percentage, or freeze condition.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `gegenstand` | `str` (Literal) | One of: `"Objekt"`, `"Text"`, `"RegEx"`, `"Bild"`, `"Sprachen"`, `"Freeze"` | What to search for; drives which other parameters become active |
| `quelldokument` | `str` (Literal) | One of: `"Bildschirm"`, `"Datei"`, `"Ergebnisfeld"` | Where to search |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `warte_vor_start_ms` | `int` | `0` | ≥ 0 | Wait time in ms before search starts |
| `timeout_ms` | `int` | — | ≥ 0; for Freeze: time between compared images | Search timeout in ms |
| `objektnummer` | `str` | — | Only for `"Objekt"` or `"Bild"` | ID of the image composition to search |
| `minimaler_score` | `float` | `0.9` | 0.0 – 1.0, step 0.05 recommended | Minimum match score threshold |
| `suchtext` | `str` | — | Only for `"Text"` or `"RegEx"` | Text or regex pattern to find |
| `gross_kleinschreibung` | `bool` | `False` | Only for `"Text"` or `"RegEx"` | Whether to match case |
| `datei` | `str` | — | Only when `quelldokument == "Datei"` | File path to search |
| `seiten` | `str` | — | Format: `"1-3"`, `"1,2,5"`, `"1-"`, `"-1"` | Pages of a multi-page file to search |
| `reihenfolge` | `str` | `"Höchstes"` | `"Höchstes"`, `"Nächstes"`, `"Zufällig"`, `"Oben nach unten"`, `"Unten nach oben"`, `"Links nach rechts"`, `"Rechts nach links"` | Ordering of result hits |
| `treffer_nr` | `int` | `1` | Negative = reversed order | Which hit to use as primary result |
| `filter` | `str` | — | `"Darunter"`, `"Darüber"`, `"Links von"`, `"Rechts von"`, `"In der Reihe von"`, `"In der Spalte von"` | Filter results by position |
| `filter_koordinate` | `float` | — | Depends on filter type | X or Y coordinate for filter |
| `ocr_profil` | `str` | `"Default"` | `"Default"`, `"Aus"`, `"Text"`, `"Tabelle"`, `"Tabelle erzwingen"` | OCR text-extraction mode (for Text/RegEx) |
| `ocr_modus` | `str` | `"Default"` | `"Default"`, `"Schnell"`, `"Genau"`, `"Feld"` | OCR analysis mode |
| `mit_neuer_aufloesung` | `int \| float` | `2` | 0 (none), 1 (auto once), 2 (dynamic), or 50–3200 dpi | DPI rescaling |
| `zoom` | `float` | `1.0` | 0.1–4.0 | Zoom factor before OCR |
| `bildverbesserung` | `str` | `"Keine"` | `"Beides"`, `"Bereinigen"`, `"Schärfen"`, `"Keine"` | Noise/sharpening pre-processing |
| `kontrast_verbessern` | `bool` | `False` | — | Local contrast enhancement |
| `text_rotation` | `str` | `"Aus"` | `"Aus"`, `"Auto"` | Auto-rotate text before OCR |
| `texttyp` | `str` | `"Default"` | `"Default"`, `"Gotisch"`, `"Nadeldrucker"`, `"Bankscheck(CMC7)"`, `"Bankscheck(E13B)"`, `"Kreditkarte(OCR A)"`, `"Maschinell(OCR B)"`, `"Quittung"`, `"Schreibmaschine"` | Font type hint for OCR |
| `sprachen` | `list[str]` | `[]` | Values from language list | OCR languages to use |
| `erweiterte_optionen` | `str` | — | `{FO:...}`, `{PROFILE:...}`, `{MODE:...}`, etc. | Advanced OCR inline config overrides |

### Enum Values

- `gegenstand`: `"Objekt"` | `"Text"` | `"RegEx"` | `"Bild"` | `"Sprachen"` | `"Freeze"`
- `quelldokument`: `"Bildschirm"` | `"Datei"` | `"Ergebnisfeld"`
- `reihenfolge`: `"Höchstes"` | `"Nächstes"` | `"Zufällig"` | `"Oben nach unten"` | `"Unten nach oben"` | `"Links nach rechts"` | `"Rechts nach links"`
- `filter`: `"Darunter"` | `"Darüber"` | `"Links von"` | `"Rechts von"` | `"In der Reihe von"` | `"In der Spalte von"`
- `ocr_profil`: `"Default"` | `"Aus"` | `"Text"` | `"Tabelle"` | `"Tabelle erzwingen"`
- `ocr_modus`: `"Default"` | `"Schnell"` | `"Genau"` | `"Feld"`
- `bildverbesserung`: `"Beides"` | `"Bereinigen"` | `"Schärfen"` | `"Keine"`
- `text_rotation`: `"Aus"` | `"Auto"`
- `texttyp`: `"Default"` | `"Gotisch"` | `"Nadeldrucker"` | `"Bankscheck(CMC7)"` | `"Bankscheck(E13B)"` | `"Kreditkarte(OCR A)"` | `"Maschinell(OCR B)"` | `"Quittung"` | `"Schreibmaschine"`
- `sprachen` values: `"Chinesisch/Taiwanesisch"`, `"Englisch"`, `"Französisch"`, `"Deutsch"`, `"Griechisch"`, `"Italienisch"`, `"Norwegisch"`, `"Portugiesisch"`, `"Russisch"`, `"Slowenisch"`, `"Kroatisch"`, `"Spanisch"`, `"Schwedisch"`, `"Türkisch"`, `"Zahlen"`, `"Ganzzahl"`, `"Dezimalzahl"`, `"Römische Zahl"`, `"Englische Zahlwörter"`, `"Währungen"`, `"Datum"`, `"Zeit 12h/24h Format"`, `"Zeit 24h Format"`

### Constraints & Validation Rules

- `objektnummer` is required when `gegenstand` is `"Objekt"` or `"Bild"`.
- `suchtext` is required when `gegenstand` is `"Text"` or `"RegEx"`.
- `gross_kleinschreibung` only applies when `gegenstand` is `"Text"` or `"RegEx"`.
- `ocr_profil`, `ocr_modus`, `texttyp`, `sprachen`, `mit_neuer_aufloesung`, `zoom`, `bildverbesserung`, `kontrast_verbessern`, `text_rotation` only apply when `gegenstand` is `"Text"` or `"RegEx"`.
- `datei` and `seiten` only apply when `quelldokument` is `"Datei"`.
- `minimaler_score` range: 0.0 ≤ value ≤ 1.0.
- The input field is highlighted red if a required parameter (e.g., `objektnummer`) is missing.
- Advanced OCR options (`erweiterte_optionen`) use inline `{KEY:VALUE}` syntax and override the tab-level settings.

### Minimal Valid Example

```json
{
  "aktionstyp": "FIND",
  "parameter": {
    "gegenstand": "Text",
    "quelldokument": "Bildschirm",
    "suchtext": "Rechnung",
    "timeout_ms": "5000",
    "minimaler_score": "0.9"
  },
  "nachfolger": ["step_002"]
}
```

### Pydantic Model Skeleton

```python
class FindParameter(BaseModel):
    gegenstand: Literal["Objekt", "Text", "RegEx", "Bild", "Sprachen", "Freeze"]
    quelldokument: Literal["Bildschirm", "Datei", "Ergebnisfeld"] = "Bildschirm"
    warte_vor_start_ms: int = 0
    timeout_ms: int | None = None
    objektnummer: str | None = None        # required if gegenstand in {"Objekt","Bild"}
    minimaler_score: float = 0.9           # 0.0–1.0
    suchtext: str | None = None            # required if gegenstand in {"Text","RegEx"}
    gross_kleinschreibung: bool = False
    datei: str | None = None
    seiten: str | None = None
    reihenfolge: str = "Höchstes"
    treffer_nr: int = 1
    filter: str | None = None
    filter_koordinate: float | None = None
    ocr_profil: str = "Default"
    ocr_modus: str = "Default"
    mit_neuer_aufloesung: int | float = 2
    zoom: float = 1.0
    bildverbesserung: str = "Keine"
    kontrast_verbessern: bool = False
    text_rotation: str = "Aus"
    texttyp: str = "Default"
    sprachen: list[str] = []
    erweiterte_optionen: str | None = None
```

---

## Action Type: FIND_AND_CLICK

**Purpose:** Performs a FIND operation and immediately executes a left click on the found object or text position; all parameters are identical to FIND.

### Required Parameters

Same as `FIND` (see above).

### Optional Parameters

Same as `FIND` (see above). No additional click-specific parameters are documented — the click is always a single left click at the crosshair position (for objects) or the center of the first matched word/group (for text/regex).

### Enum Values

Same as `FIND`.

### Constraints & Validation Rules

- All constraints from FIND apply.
- The click position for an object search is the crosshair defined at object creation time.
- The click position for a text search is the center of the first matched word; for RegEx, the center of the first captured group.
- No additional click options (right-click, double-click, duration) are exposed on this step type — use FIND + CLICK separately for those.

### Minimal Valid Example

```json
{
  "aktionstyp": "FIND_AND_CLICK",
  "parameter": {
    "gegenstand": "Objekt",
    "quelldokument": "Bildschirm",
    "objektnummer": "42",
    "timeout_ms": "8000",
    "minimaler_score": "0.85"
  },
  "nachfolger": ["step_003"]
}
```

### Pydantic Model Skeleton

```python
class FindAndClickParameter(FindParameter):
    pass  # Identical parameter set to FindParameter
```

---

## Action Type: CLICK

**Purpose:** Executes a mouse click (left, right, double, or mouse-over) at specified screen coordinates.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `x` | `float` | ≥ 0, pixels | X coordinate for click (0 = top-left) |
| `y` | `float` | ≥ 0, pixels | Y coordinate for click |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `versatz_x` | `float` | `0.0` | Positive = right | X offset from referenced step coordinate |
| `versatz_y` | `float` | `0.0` | Positive = down | Y offset from referenced step coordinate |
| `dauer_ms` | `int` | `0` | ≥ 0 | Hold duration in ms before releasing mouse button |
| `doppelklick` | `bool` | `False` | — | Whether to execute a double click |
| `rechtsklick` | `bool` | `False` | — | Whether to click the right mouse button instead of left |
| `nur_mouseover` | `bool` | `False` | — | Move cursor only; no click is executed |

### Enum Values

None — all boolean flags.

### Constraints & Validation Rules

- If `nur_mouseover` is `True`, both `doppelklick` and `rechtsklick` are ignored.
- `x` and `y` can come from a constant value, from a referenced step's result field (e.g., X/Y of a FIND step), or from a variable.
- Coordinates are in pixels; origin is upper-left corner of the screen.

### Minimal Valid Example

```json
{
  "aktionstyp": "CLICK",
  "parameter": {
    "x": "500",
    "y": "300",
    "doppelklick": "false",
    "rechtsklick": "false"
  },
  "nachfolger": ["step_004"]
}
```

### Pydantic Model Skeleton

```python
class ClickParameter(BaseModel):
    x: float
    y: float
    versatz_x: float = 0.0
    versatz_y: float = 0.0
    dauer_ms: int = 0
    doppelklick: bool = False
    rechtsklick: bool = False
    nur_mouseover: bool = False
```

---

## Action Type: DRAG

**Purpose:** Clicks and holds the mouse button at a start coordinate, drags to an end coordinate, and releases — used for drag-and-drop operations.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `start_x` | `float` | ≥ 0, pixels | X coordinate where mouse button is pressed |
| `start_y` | `float` | ≥ 0, pixels | Y coordinate where mouse button is pressed |
| `ende_x` | `float` | ≥ 0, pixels | X coordinate where mouse button is released |
| `ende_y` | `float` | ≥ 0, pixels | Y coordinate where mouse button is released |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `start_versatz_x` | `float` | `0.0` | Positive = right | X offset from a referenced step's start coordinate |
| `start_versatz_y` | `float` | `0.0` | Positive = down | Y offset from a referenced step's start coordinate |
| `ende_versatz_x` | `float` | `0.0` | Positive = right | X offset from a referenced step's end coordinate |
| `ende_versatz_y` | `float` | `0.0` | Positive = down | Y offset from a referenced step's end coordinate |

### Enum Values

None.

### Constraints & Validation Rules

- All coordinates are in pixels; origin at top-left.
- Coordinates can be constant values, result fields from prior steps, or variables (Dezimalzahl type).

### Minimal Valid Example

```json
{
  "aktionstyp": "DRAG",
  "parameter": {
    "start_x": "100",
    "start_y": "200",
    "ende_x": "400",
    "ende_y": "200"
  },
  "nachfolger": ["step_005"]
}
```

### Pydantic Model Skeleton

```python
class DragParameter(BaseModel):
    start_x: float
    start_y: float
    ende_x: float
    ende_y: float
    start_versatz_x: float = 0.0
    start_versatz_y: float = 0.0
    ende_versatz_x: float = 0.0
    ende_versatz_y: float = 0.0
```

---

## Action Type: SCROLL

**Purpose:** Scrolls the screen or an application window up, down, left, or right by a number of click steps or pixels.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `gegenstand` | `str` (Literal) | `"Klick"` or `"Pixel"` | Whether `schritte` counts mouse wheel clicks or pixels |
| `richtung` | `str` (Literal) | `"Links"`, `"Rechts"`, `"Hoch"`, `"Runter"` | Scroll direction |
| `schritte` | `int` | ≥ 1 | Number of scroll clicks or pixels |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `warte_vor_start_ms` | `int` | `0` | ≥ 0 | Wait before scrolling in ms |
| `start_x` | `float` | — | ≥ 0, pixels | X position to move cursor to before scrolling |
| `start_y` | `float` | — | ≥ 0, pixels | Y position to move cursor to before scrolling |

### Enum Values

- `gegenstand`: `"Klick"` | `"Pixel"`
- `richtung`: `"Links"` | `"Rechts"` | `"Hoch"` | `"Runter"`

### Constraints & Validation Rules

- When `gegenstand` is `"Klick"`, Windows typically scrolls 3 lines/columns per click step.
- `start_x` / `start_y` determine where the cursor is positioned before the scroll.

### Minimal Valid Example

```json
{
  "aktionstyp": "SCROLL",
  "parameter": {
    "gegenstand": "Klick",
    "richtung": "Runter",
    "schritte": "3",
    "start_x": "640",
    "start_y": "400"
  },
  "nachfolger": ["step_006"]
}
```

### Pydantic Model Skeleton

```python
class ScrollParameter(BaseModel):
    gegenstand: Literal["Klick", "Pixel"]
    richtung: Literal["Links", "Rechts", "Hoch", "Runter"]
    schritte: int
    warte_vor_start_ms: int = 0
    start_x: float | None = None
    start_y: float | None = None
```

---

## Action Type: TYPE

**Purpose:** Sends keyboard input (text, key combinations, and mouse events) to the active application window.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `eingabetext` | `str` | — | Text and/or key codes to send |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `key_basiertes_tippen` | `bool` | `False` | — | `True` = send as keystroke events (supports Remote Desktop/Citrix); `False` = paste as text block |
| `text_unveraendert_eingeben` | `bool` | `False` | — | `True` = send text literally without interpreting special codes |

### Enum Values

None — boolean flags plus free-form string with embedded key codes.

### Constraints & Validation Rules

- Special characters in `eingabetext` with `key_basiertes_tippen=True`: `+` = Shift, `^` = Ctrl, `%` = Alt, `~` = Enter; literal `{+}`, `{^}`, `{%}`, `{~}` to enter these.
- Key codes use `{KEYNAME}` syntax, e.g., `{ENTER}`, `{TAB}`, `{F1}`.
- Repetition: `{LEFT 42}` = press LEFT 42 times; `(text 3)` = repeat sequence 3 times.
- Delay injection: `{300}` = wait 300 ms at that position.
- Mouse events in TYPE: `{CLICK}`, `{RCLICK}`, `{DCLICK}`, `{CLICK(x,y,duration)}`.
- When `text_unveraendert_eingeben=True`, no special codes are interpreted.
- Using `{CV:varname}` injects a variable's value; `{SR:stepId:fieldname}` injects a step result.
- Modifier combinations: `{SHIFT}(EC)` holds Shift while pressing E and C.
- If `eingabetext` has malformed braces, the step produces no output without error.
- Shorthand modifiers (`+`, `^`, `%`) only work when `key_basiertes_tippen=False`.

### Minimal Valid Example

```json
{
  "aktionstyp": "TYPE",
  "parameter": {
    "eingabetext": "Hello{TAB}World{ENTER}",
    "key_basiertes_tippen": "false"
  },
  "nachfolger": ["step_007"]
}
```

### Pydantic Model Skeleton

```python
class TypeParameter(BaseModel):
    eingabetext: str
    key_basiertes_tippen: bool = False
    text_unveraendert_eingeben: bool = False
```

---

## Action Type: READ

**Purpose:** Reads text or an image from a defined rectangular region on the screen, from a file, or from another step's result field.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `gegenstand` | `str` (Literal) | `"Text"`, `"Text-Field"`, `"Objekt"` | What to read |
| `referenz_x` | `float` | pixels or mm | X coordinate of the center of the read region |
| `referenz_y` | `float` | pixels or mm | Y coordinate of the center of the read region |
| `breite` | `float` | > 0 | Width of the read region |
| `hoehe` | `float` | > 0 | Height of the read region |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `warte_vor_start_ms` | `int` | `0` | ≥ 0 | Wait before reading |
| `timeout_ms` | `int` | — | ≥ 0 | Max OCR time |
| `versatz_x` | `float` | `0.0` | — | X offset from reference point |
| `versatz_y` | `float` | `0.0` | — | Y offset from reference point |
| `in_zwischenablage` | `bool` | `False` | — | Copy read result to clipboard |
| `quelldokument` | `str` (Literal) | `"Bildschirm"` | `"Bildschirm"` or `"Datei"` | Source of image data |
| `datei` | `str` | — | Only if `quelldokument == "Datei"` | File path |
| `seite` | `int` | — | Only for multi-page files | Page number |
| `validierungsmuster` | `str` | — | RegEx | Valid result pattern; step fails if result does not match |
| `ocr_profil` | `str` | `"Default"` | Same values as FIND | OCR profile |
| `ocr_modus` | `str` | `"Default"` | Same values as FIND | OCR mode |
| `mit_neuer_aufloesung` | `int \| float` | `2` | 0,1,2, or 50–3200 | DPI rescaling |
| `zoom` | `float` | `1.0` | 0.1–4.0 | Zoom factor |
| `bildverbesserung` | `str` | `"Keine"` | Same values as FIND | Noise/sharpening |
| `kontrast_verbessern` | `bool` | `False` | — | Local contrast enhancement |
| `text_rotation` | `str` | `"Aus"` | `"Aus"`, `"Auto"` | Auto-rotate text |
| `texttyp` | `str` | `"Default"` | Same values as FIND | Font type hint |
| `sprachen` | `list[str]` | `[]` | Same values as FIND + email/address types for Text-Field | OCR languages |
| `obere_tiefenschaerfe` | `int` | `200` | 0–1000 | Max contrast (Shape mode for Objekt) |
| `untere_tiefenschaerfe` | `int` | `50` | 0–1000 | Min contrast (Shape mode for Objekt) |
| `min_uebereinstimmung` | `float` | `2.0` | 0.0–100.0 | Minimum contrast match % (Shape mode) |

### Enum Values

- `gegenstand`: `"Text"` | `"Text-Field"` | `"Objekt"`
- `quelldokument`: `"Bildschirm"` | `"Datei"`
- `ocr_profil`: `"Default"` | `"None"` | `"Text"` | `"Table"` | `"ForceTables"` (note: English names in Lesen section)
- `ocr_modus`: `"Default"` | `"Fast"` | `"Accurate"` | `"Field"` (English names in Lesen section)
- `text_rotation`: `"Aus"` | `"Auto"`

### Constraints & Validation Rules

- `referenz_x`, `referenz_y`, `breite`, `hoehe`, `versatz_x`, `versatz_y` can be constant values, result fields from prior steps, or Dezimalzahl variables.
- The `obere_tiefenschaerfe`, `untere_tiefenschaerfe`, and `min_uebereinstimmung` parameters are only used when `gegenstand == "Objekt"` (Shape configuration tab).
- `validierungsmuster` also assists OCR accuracy — providing a RegEx tells EMMA to prioritize digit recognition at `\d` positions, etc.
- Extra OCR languages for `"Text-Field"` gegenstand: `"E-Mail"`, `"Adresse (UK)"`, `"Adresse (US)"`, `"Adresse (FR)"`, `"Adresse (DE)"`.
- Advanced inline options `{FO:...}`, `{PROFILE:...}` etc. can be appended to a text field.

### Minimal Valid Example

```json
{
  "aktionstyp": "READ",
  "parameter": {
    "gegenstand": "Text",
    "quelldokument": "Bildschirm",
    "referenz_x": "640",
    "referenz_y": "400",
    "breite": "200",
    "hoehe": "30",
    "timeout_ms": "5000"
  },
  "nachfolger": ["step_008"]
}
```

### Pydantic Model Skeleton

```python
class ReadParameter(BaseModel):
    gegenstand: Literal["Text", "Text-Field", "Objekt"]
    referenz_x: float
    referenz_y: float
    breite: float
    hoehe: float
    warte_vor_start_ms: int = 0
    timeout_ms: int | None = None
    versatz_x: float = 0.0
    versatz_y: float = 0.0
    in_zwischenablage: bool = False
    quelldokument: Literal["Bildschirm", "Datei"] = "Bildschirm"
    datei: str | None = None
    seite: int | None = None
    validierungsmuster: str | None = None
    ocr_profil: str = "Default"
    ocr_modus: str = "Default"
    mit_neuer_aufloesung: int | float = 2
    zoom: float = 1.0
    bildverbesserung: str = "Keine"
    kontrast_verbessern: bool = False
    text_rotation: str = "Aus"
    texttyp: str = "Default"
    sprachen: list[str] = []
    obere_tiefenschaerfe: int = 200    # Objekt only
    untere_tiefenschaerfe: int = 50    # Objekt only
    min_uebereinstimmung: float = 2.0  # Objekt only
```

---

## Action Type: READ_FORM

**Purpose:** Reads structured data from a document (PDF or image) by matching it against a pre-configured document template (Dokumentvorlage) and extracting field values.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `form_id` | `str` | Non-empty | ID of the document template (Dokumentvorlage) |
| `input_file` | `str` | Non-empty; PDF, JPEG, BMP, or PNG | Path to the document file to read |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `page_to_read` | `int` | `1` | Ignored for non-PDF files | Page to analyse in multi-page documents |

### Enum Values

None.

### Constraints & Validation Rules

- The Dokumentvorlage must be created and stored in EMMA's Document Repository first.
- `input_file` must be PDF, JPEG, Bitmap, or PNG.
- `page_to_read` is ignored for JPG/PNG (single-page formats).
- Documents rotated more than 30° in one direction will not be read correctly.
- Best practice: make extraction regions larger than the actual form fields, because users write outside boundaries.
- Results are best processed by a downstream IMPORT step.

### Minimal Valid Example

```json
{
  "aktionstyp": "READ_FORM",
  "parameter": {
    "form_id": "FORM_001",
    "input_file": "C:\\Documents\\invoice.pdf",
    "page_to_read": "1"
  },
  "nachfolger": ["step_009"]
}
```

### Pydantic Model Skeleton

```python
class ReadFormParameter(BaseModel):
    form_id: str
    input_file: str
    page_to_read: int = 1
```

---

## Action Type: GENAI

**Purpose:** Executes an EMMA Cortex Skill (generative AI task) by sending input data to a configured LLM and capturing structured output fields.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `skill` | `str` | Non-empty; must be a valid Skill ID from EMMA Cortex Admin | The Cortex Skill to execute |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `skill_inputs` | `dict[str, str]` | `{}` | Keys and values correspond to the Skill's defined input variables | Dynamic input fields populated after Skill selection |
| `save_to_csv` | `bool` | `False` | — | Whether to save output to a CSV file at `%AppData%\OTTRobotics\EMMA Studio\SkillsOutput` |

### Enum Values

None (Skill IDs are dynamic, not a fixed enum).

### Constraints & Validation Rules

- Requires the EMMA Cortex add-on to be installed and licensed (license codes: 1900, 1901, 1902).
- The EMMA Cortex Service must be running.
- At least one Skill must exist in EMMA Cortex Admin.
- User must have the "Skill" permission.
- Input fields are dynamically determined by the selected Skill's definition — they are not statically enumerable.
- Output fields are also dynamic; downstream consumption is typically via an IMPORT step with source `"GenAI Step"`.
- Processing time varies by model (cloud vs. local).

### Minimal Valid Example

```json
{
  "aktionstyp": "GENAI",
  "parameter": {
    "skill": "invoice_extraction_v1",
    "save_to_csv": "false"
  },
  "nachfolger": ["step_010"]
}
```

### Pydantic Model Skeleton

```python
class GenAIParameter(BaseModel):
    skill: str
    skill_inputs: dict[str, str] = {}
    save_to_csv: bool = False
```

---

## Action Type: EXPORT

**Purpose:** Writes a single value to a specified cell in an XLSX or CSV file at runtime.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `datei` | `str` | Non-empty; `.xlsx` or `.csv` | Full path of the target file |
| `spalte` | `str` | Non-empty | Column identifier for the target cell |
| `zeile` | `int` | ≥ 1 | Row number for the target cell |
| `wert` | `str` | — | The value to write |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `gegenstand` | `str` | `"Zelle"` | Currently only `"Zelle"` supported | What to export (currently single-cell only) |
| `tabelle` | `int` | `1` | ≥ 1 | Worksheet number (Excel only) |
| `trennzeichen` | `str` | `","` | Typically `","` or `";"` | CSV delimiter |
| `erste_zeile_ignorieren` | `bool` | `False` | — | Skip first row (header row) |

### Enum Values

- `gegenstand`: currently only `"Zelle"` (single cell); other modes may be added in future.

### Constraints & Validation Rules

- Data is written as unformatted text.
- `tabelle` applies only to Excel files; ignored for CSV.
- `trennzeichen` applies only to CSV files; ignored for Excel.

### Minimal Valid Example

```json
{
  "aktionstyp": "EXPORT",
  "parameter": {
    "datei": "C:\\Reports\\output.xlsx",
    "spalte": "B",
    "zeile": "5",
    "wert": "Processed",
    "tabelle": "1"
  },
  "nachfolger": ["step_011"]
}
```

### Pydantic Model Skeleton

```python
class ExportParameter(BaseModel):
    datei: str
    spalte: str
    zeile: int
    wert: str
    gegenstand: str = "Zelle"
    tabelle: int = 1
    trennzeichen: str = ","
    erste_zeile_ignorieren: bool = False
```

---

## Action Type: IMPORT

**Purpose:** Reads one or more values (a cell, row, column, or full row/column) from an XLSX or CSV file into EMMA's result field.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `gegenstand` | `str` (Literal) | See enum values | What to import |
| `datei` | `str` | Non-empty; `.xls`, `.xlsx`, `.xlsm`, or `.csv` | Full path of the source file |
| `spalte` | `str` | Non-empty | Starting column |
| `zeile` | `int` | ≥ 1 | Starting row |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `tabelle` | `int` | `1` | ≥ 1; Excel only | Worksheet number |
| `trennzeichen` | `str` | `","` | CSV only | CSV delimiter |
| `erste_zeile_ignorieren` | `bool` | `False` | — | Exclude header row from import |
| `letzte_spalte` | `str` | — | Only for `"Zeile"` | Last column to include |
| `letzte_zeile` | `int` | — | Only for `"Spalte"` | Last row to include |
| `timeout_ms` | `int` | — | ≥ 0 | Max wait time if file is locked |

### Enum Values

- `gegenstand`: `"Zelle"` | `"Zeile"` | `"Spalte"` | `"Ganze Zeile"` | `"Ganze Spalte"`

### Constraints & Validation Rules

- `tabelle` applies to Excel (`.xls`, `.xlsx`, `.xlsm`) only; ignored for CSV.
- `trennzeichen` applies to CSV only.
- Formatted but empty trailing fields at end of a row/column are not imported.
- `letzte_spalte` is only relevant when `gegenstand == "Zeile"`.
- `letzte_zeile` is only relevant when `gegenstand == "Spalte"`.
- The source can also be `"GenAI Step"` result output (selected in the source document field of EMMA Studio UI).

### Minimal Valid Example

```json
{
  "aktionstyp": "IMPORT",
  "parameter": {
    "gegenstand": "Zelle",
    "datei": "C:\\Data\\input.csv",
    "spalte": "A",
    "zeile": "2",
    "trennzeichen": ";"
  },
  "nachfolger": ["step_012"]
}
```

### Pydantic Model Skeleton

```python
class ImportParameter(BaseModel):
    gegenstand: Literal["Zelle", "Zeile", "Spalte", "Ganze Zeile", "Ganze Spalte"]
    datei: str
    spalte: str
    zeile: int
    tabelle: int = 1
    trennzeichen: str = ","
    erste_zeile_ignorieren: bool = False
    letzte_spalte: str | None = None    # only for gegenstand == "Zeile"
    letzte_zeile: int | None = None     # only for gegenstand == "Spalte"
    timeout_ms: int | None = None
```

---

## Action Type: FILE_OPERATION

**Purpose:** Performs file and directory management operations: naming, opening, copying, moving, deleting files, and managing directories.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `gegenstand` | `str` (Literal) | See enum values | Operation to perform |
| `quelle` | `str` | Non-empty | Directory where the source file resides |
| `dateiname` | `str` | Non-empty; may contain wildcards like `*.pdf` | File name or pattern |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `sortierung` | `str` | — | `"Name aufsteigend"`, `"Name absteigend"`, `"Datum aufsteigend"`, `"Datum absteigend"`, `"Größe aufsteigend"`, `"Größe absteigend"` | Sort order when pattern returns multiple matches |
| `position` | `int` | `1` | ≥ 1 | Which file in sorted match list to operate on |
| `ziel` | `str` | — | Required for `"Datei kopieren"`, `"Datei verschieben"`, `"Verzeichnis zippen"` | Target directory |
| `ueberschreiben` | `bool` | `False` | For copy/move/zip operations | Whether to overwrite existing file at destination |
| `neuer_dateiname` | `str` | — | For copy/move/zip; optional | New file name at destination; original name kept if empty |

### Enum Values

- `gegenstand`: `"Datei Name"` | `"Datei öffnen"` | `"Datei kopieren"` | `"Datei verschieben"` | `"Datei löschen"` | `"Verzeichnis Name"` | `"Verzeichnis öffnen"` | `"Verzeichnis verschieben"` | `"Verzeichnis zippen"`
- `sortierung`: `"Name aufsteigend"` | `"Name absteigend"` | `"Änderungsdatum aufsteigend"` | `"Änderungsdatum absteigend"` | `"Größe aufsteigend"` | `"Größe absteigend"`

### Constraints & Validation Rules

- `ziel` is required when `gegenstand` is `"Datei kopieren"`, `"Datei verschieben"`, or `"Verzeichnis zippen"`.
- `ueberschreiben` applies to `"Datei kopieren"`, `"Datei verschieben"`, `"Verzeichnis verschieben"`, and `"Verzeichnis zippen"`.
- `neuer_dateiname` applies to `"Datei kopieren"`, `"Datei verschieben"`, and `"Verzeichnis zippen"`.
- When a wildcard pattern is used and multiple files match, `sortierung` and `position` determine which file is selected.
- `"Datei Name"` returns the file name in the "Gefundener Text" result field and the file count in the result count.

### Minimal Valid Example

```json
{
  "aktionstyp": "FILE_OPERATION",
  "parameter": {
    "gegenstand": "Datei kopieren",
    "quelle": "C:\\Input",
    "dateiname": "report.pdf",
    "ziel": "C:\\Archive",
    "ueberschreiben": "false"
  },
  "nachfolger": ["step_013"]
}
```

### Pydantic Model Skeleton

```python
class FileOperationParameter(BaseModel):
    gegenstand: Literal[
        "Datei Name", "Datei öffnen", "Datei kopieren", "Datei verschieben",
        "Datei löschen", "Verzeichnis Name", "Verzeichnis öffnen",
        "Verzeichnis verschieben", "Verzeichnis zippen"
    ]
    quelle: str
    dateiname: str
    sortierung: str | None = None
    position: int = 1
    ziel: str | None = None
    ueberschreiben: bool = False
    neuer_dateiname: str | None = None
```

---

## Action Type: SEND_MAIL

**Purpose:** Sends an email with configurable recipients, subject, body text, and attachment via a pre-configured SMTP server.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `mail_an` | `str` | Non-empty; multiple addresses separated by `";"` | Primary recipient(s) |
| `betreff` | `str` | — | Email subject |
| `mail_text` | `str` | — | Email body text; supports `{CV:varname}` and `{SR:step:field}` syntax |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `cc` | `str` | — | Multiple addresses by `";"` | CC recipients |
| `bcc` | `str` | — | Multiple addresses by `";"` | BCC recipients |
| `anhang` | `str` | — | File path | Email attachment |

### Enum Values

None.

### Constraints & Validation Rules

- SMTP server must be configured in EMMA Configuration (global settings) before this step can work.
- Multiple email addresses in any address field must be separated by `";"`.
- `mail_text` supports the same variable/result-field reference syntax as the TYPE step.

### Minimal Valid Example

```json
{
  "aktionstyp": "SEND_MAIL",
  "parameter": {
    "mail_an": "recipient@example.com",
    "betreff": "Process completed",
    "mail_text": "The process finished at {CV:timestamp}."
  },
  "nachfolger": ["step_014"]
}
```

### Pydantic Model Skeleton

```python
class SendMailParameter(BaseModel):
    mail_an: str
    betreff: str
    mail_text: str
    cc: str | None = None
    bcc: str | None = None
    anhang: str | None = None
```

---

## Action Type: COMMAND

**Purpose:** Executes an arbitrary command-line instruction, optionally capturing console output and optionally waiting for the process to finish.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `dateiname` | `str` | Non-empty; must be on system PATH or relative to `arbeitsverzeichnis` | Executable or script to launch (e.g., `chrome.exe`) |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `arbeitsverzeichnis` | `str` | — | Must be a valid directory path | Working directory for command execution |
| `argumente` | `str` | — | — | Arguments to pass to the executable |
| `versteckt` | `bool` | `False` | — | Run without showing a window |
| `ende_abwarten` | `bool` | `True` | — | Whether EMMA waits for the process to finish |
| `capture_output` | `str` | `"No"` | Only if `ende_abwarten=True` | Which output stream(s) to capture as "Gefundener Text" |

### Enum Values

- `capture_output`: `"No"` | `"Output"` | `"Error"` | `"Both"`

### Constraints & Validation Rules

- `capture_output` is only relevant when `ende_abwarten` is `True`.
- If `ende_abwarten` is `False`, the command runs in the background and EMMA continues immediately; `capture_output` is effectively ignored.
- External programs launched via URL (e.g., `https://...`) also work as `dateiname`.

### Minimal Valid Example

```json
{
  "aktionstyp": "COMMAND",
  "parameter": {
    "dateiname": "python.exe",
    "arbeitsverzeichnis": "C:\\Scripts",
    "argumente": "process.py --mode prod",
    "ende_abwarten": "true",
    "capture_output": "Output"
  },
  "nachfolger": ["step_015"]
}
```

### Pydantic Model Skeleton

```python
class CommandParameter(BaseModel):
    dateiname: str
    arbeitsverzeichnis: str | None = None
    argumente: str | None = None
    versteckt: bool = False
    ende_abwarten: bool = True
    capture_output: Literal["No", "Output", "Error", "Both"] = "No"
```

---

## Action Type: LOOP

**Purpose:** Repeats a set of steps a bounded number of times; acts as a counter-controlled loop with configurable reset behaviour.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `maximale_anzahl_loops` | `int` | ≥ 1 | Maximum number of iterations before the loop exits |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `bei_max_zuruecksetzen` | `bool` | `False` | — | Reset counter when maximum is reached (useful for multi-column Excel reads) |
| `vor_start_zuruecksetzen` | `bool` | `False` | — | Reset counter to 0 when the loop step is entered |

### Enum Values

None.

### Constraints & Validation Rules

- A loop must always specify `maximale_anzahl_loops` to prevent infinite loops.
- The loop step itself acts as a branch point: its `nachfolger` list must have exactly **two** entries — the first pointing inside the loop body (taken when the counter has not yet reached maximum), the second pointing to the step after the loop (taken when maximum is reached).
- **Branch semantics for LOOP**: in the DECISION/branch condition table, `"Falsch"` maps to the next step *inside* the loop body, and `"Wahr"` maps to the step *outside* (continuation after loop completion).
- A loop is logged as "nicht erfolgreich" if exited before reaching the maximum.
- A loop is logged as "erfolgreich" when it reaches the maximum iteration count.
- The loop counter is accessible via the step result field and can be used in downstream IMPORT steps (e.g., for Excel row numbers).
- `vor_start_zuruecksetzen` combined with a Boolean variable allows re-entry from zero.

### Minimal Valid Example

```json
{
  "aktionstyp": "LOOP",
  "parameter": {
    "maximale_anzahl_loops": "10",
    "bei_max_zuruecksetzen": "false",
    "vor_start_zuruecksetzen": "false"
  },
  "nachfolger": ["step_loop_body_001", "step_after_loop"]
}
```

### Pydantic Model Skeleton

```python
class LoopParameter(BaseModel):
    maximale_anzahl_loops: int
    bei_max_zuruecksetzen: bool = False
    vor_start_zuruecksetzen: bool = False
```

---

## Action Type: DECISION

**Purpose:** Evaluates an ordered list of Boolean rules; each rule that evaluates to true routes execution to its associated successor step. Implements arbitrary n-way branching.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `verzweigungstyp` | `str` (Literal) | See enum values | Data type used to evaluate all rules in this Decision |
| `regeln` | `list[DecisionRule]` | ≥ 1 rule | Ordered list of decision rules |

### DecisionRule sub-structure

| Field | Python Type | Description |
|-------|-------------|-------------|
| `linker_wert` | `str` | Left operand; constant, variable reference, or step result field |
| `relation` | `str` | Comparison operator (type-dependent, see enum) |
| `rechter_wert` | `str` | Right operand |
| `nachfolger_id` | `str` | ID of the step to execute when this rule evaluates to `true` |

### Optional Parameters

None at the top level; however, it is strongly recommended to add a final "catch-all" rule (e.g., `1 = 1`) that always fires, to prevent process abort.

### Enum Values

- `verzweigungstyp`: `"Boolean"` | `"Ganzzahl"` | `"Dezimalzahl"` | `"Text"` | `"Datum&Uhrzeit"`
- `relation` (Boolean): `"="` | `"!="`
- `relation` (Ganzzahl, Dezimalzahl, Datum&Uhrzeit): `"="` | `"!="` | `"<"` | `"<="` | `">"` | `">="`
- `relation` (Text): `"="` | `"!="` | `"Beinhaltet"` | `"Startet mit"` | `"Endet mit"`

### Constraints & Validation Rules

- Rules are evaluated **in order** (top to bottom); the first rule that is `true` wins and all subsequent rules are skipped.
- If no rule fires, the process aborts. Always add a fallback rule.
- `"="` for Text requires full string equality (all characters must match).
- `"Beinhaltet"` checks if the right value is a substring of the left value.
- Operands can be constant values, variables, or step result fields (selectable via right-click context menu).
- Each rule in the list contributes one `nachfolger_id`, so the set of all unique `nachfolger_id` values from the rules together with the DECISION step's own `nachfolger` list defines the outgoing edges.

### Minimal Valid Example

```json
{
  "aktionstyp": "DECISION",
  "parameter": {
    "verzweigungstyp": "Text",
    "regeln": [
      {
        "linker_wert": "{CV:status}",
        "relation": "=",
        "rechter_wert": "OK",
        "nachfolger_id": "step_ok"
      },
      {
        "linker_wert": "{CV:status}",
        "relation": "=",
        "rechter_wert": "FEHLER",
        "nachfolger_id": "step_error"
      },
      {
        "linker_wert": "1",
        "relation": "=",
        "rechter_wert": "1",
        "nachfolger_id": "step_default"
      }
    ]
  },
  "nachfolger": ["step_ok", "step_error", "step_default"]
}
```

### Pydantic Model Skeleton

```python
class DecisionRule(BaseModel):
    linker_wert: str
    relation: str
    rechter_wert: str
    nachfolger_id: str

class DecisionParameter(BaseModel):
    verzweigungstyp: Literal["Boolean", "Ganzzahl", "Dezimalzahl", "Text", "Datum&Uhrzeit"]
    regeln: list[DecisionRule]
```

---

## Action Type: WAIT

**Purpose:** Pauses process execution for a fixed time, until a user confirms a dialog, or until a user provides text input.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `gegenstand` | `str` (Literal) | `"Zeit"`, `"Bestätigung"`, `"Eingabe"` | What to wait for |
| `timeout_ms` | `int` | ≥ 0; 0 = infinite (user action required) | Wait duration; at expiry, step completes as "nicht erfolgreich" if no user action taken |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `meldung` | `str` | — | Only for `"Bestätigung"` and `"Eingabe"`; first 50 chars = dialog title | Message shown in the confirmation/input dialog |

### Enum Values

- `gegenstand`: `"Zeit"` | `"Bestätigung"` | `"Eingabe"`

### Constraints & Validation Rules

- For `"Zeit"`: process continues automatically after `timeout_ms` with successful status.
- For `"Bestätigung"`: a confirmation dialog opens; process continues after user confirms OR after timeout (with "nicht erfolgreich" status if timed out).
- For `"Eingabe"`: an input dialog opens; user-entered text is available as step result; process continues after user submits OR after timeout.
- `timeout_ms = 0` means infinite wait — user action is mandatory.
- `meldung` first 50 characters are used as the dialog window title.

### Minimal Valid Example

```json
{
  "aktionstyp": "WAIT",
  "parameter": {
    "gegenstand": "Zeit",
    "timeout_ms": "3000"
  },
  "nachfolger": ["step_016"]
}
```

### Pydantic Model Skeleton

```python
class WaitParameter(BaseModel):
    gegenstand: Literal["Zeit", "Bestätigung", "Eingabe"]
    timeout_ms: int
    meldung: str | None = None
```

---

## Action Type: SUCCESS

**Purpose:** Marks the successful end of a process; every process must have at least one SUCCESS step, analogous to START which marks the beginning.

### Required Parameters

None.

### Optional Parameters

None.

### Enum Values

None.

### Constraints & Validation Rules

- A process without at least one SUCCESS step will be treated as aborted.
- SUCCESS is always a leaf node (no outgoing edges / nachfolger).
- Multiple SUCCESS steps are allowed (e.g., one per branch of a DECISION).
- There is no FAILURE/ERROR terminal action type documented in the handbook; process failure is indicated by a step not being "erfolgreich" at runtime, not by a dedicated terminal step.

### Minimal Valid Example

```json
{
  "aktionstyp": "SUCCESS",
  "parameter": {},
  "nachfolger": []
}
```

### Pydantic Model Skeleton

```python
class SuccessParameter(BaseModel):
    pass  # No parameters
```

---

## Additional Action Types Found in Handbook

### Action Type: NESTED_PROCESS [NEW — not yet in enum]

**Purpose:** Calls a pre-defined EMMA process as a sub-process, passing variables in and out according to their interface configuration.

### Required Parameters

| Parameter | Python Type | Constraints | Description |
|-----------|-------------|-------------|-------------|
| `prozess_id` | `int` | ≥ 1; `-1` if not configured (shows red) | ID of the nested process to call |

### Optional Parameters

| Parameter | Python Type | Default | Constraints | Description |
|-----------|-------------|---------|-------------|-------------|
| `variablen` | `dict[str, str]` | `{}` | Only variables with interface `Eingehend`, `Ausgehend`, or `Ein/Aus` | Variable mappings between calling process and sub-process |

### Constraints & Validation Rules

- The step is shown grey if no process ID is selected; red if the ID is invalid or cannot be loaded.
- Only variables whose interface is set to `Eingehend`, `Ausgehend`, or `Ein/Aus` are visible for mapping.
- Green marking = flow from parent to child; Yellow = child to parent; Red = bidirectional.
- Variable flow is strictly between parent and nested process; nested process cannot access grandparent variables directly.
- The "Prozess öffnen" button appears in the results panel after first execution.

### Minimal Valid Example

```json
{
  "aktionstyp": "NESTED_PROCESS",
  "parameter": {
    "prozess_id": "42",
    "variablen": {
      "kunden_nr": "{CV:kunden_nr}",
      "ergebnis": ""
    }
  },
  "nachfolger": ["step_019"]
}
```

### Pydantic Model Skeleton

```python
class NestedProcessParameter(BaseModel):
    prozess_id: int
    variablen: dict[str, str] = {}
```

---

## Cross-Cutting Section A: `nachfolger` Semantics

**What `nachfolger` represents generally:**
`nachfolger` is the list of successor action IDs that EMMA will consider for execution after the current action completes. Each element is an `aktion_id` from the same process (Algorithmusabschnitt / Prozess). The actual next step selected depends on the step type and its branching condition outcome.

**Is it always an `aktion_id` from the same `Algorithmusabschnitt`?**
Yes. The handbook describes all step connections as intra-process edges. The "Nächster Schritt ID" result field contains the integer ID of the next step selected, and this is always within the same process. Cross-process calls use the NESTED_PROCESS step type, not `nachfolger`.

**Sentinel value for end-of-flow:**
The handbook does not document a sentinel string in `nachfolger`. The SUCCESS step naturally has no outgoing edges (empty `nachfolger`). In the team's data model, `["END"]` is used as the sentinel by convention. This is consistent with SUCCESS being a leaf node. **Correction / confirmation:** the handbook does not contradict `["END"]` as sentinel — it is safe to retain this convention.

**Typical `nachfolger` count for a linear action:**
For a normal linear action (FIND, CLICK, READ, TYPE, etc.), `nachfolger` has **one** element: the ID of the next step. However, most step types have implicit two-outcome branching: steps can route to different successors depending on whether they were "erfolgreich" (successful) or not. This is configured in the General Step Properties ("Bedingungen für den nächsten Schritt"). Thus even for a linear step, the UI allows up to two outgoing edges for the Wahr/Falsch outcomes.

**Practical model implication:** `nachfolger` in the current `EmmaAktion` model is `list[str]`. For linear steps, this will normally have 1 entry; for DECISION or LOOP steps, it will have N entries corresponding to the N branch targets.

---

## Cross-Cutting Section B: DECISION Branching

**How many successors does DECISION have?**
An arbitrary number — the handbook states "eine beliebige Anzahl von Regeln". Each rule in the rule list specifies its own successor step ID, so there are as many distinct successors as there are unique `nachfolger_id` values across all rules.

**How are branches distinguished?**
Each rule in the ordered rule list has its own target step ID. Rules are evaluated top to bottom; the first true rule fires and its target is followed. All other rules are then skipped.

**What parameters encode the branching condition?**
- `verzweigungstyp`: the data type for evaluation (`"Boolean"`, `"Ganzzahl"`, `"Dezimalzahl"`, `"Text"`, `"Datum&Uhrzeit"`)
- `regeln`: ordered list of `{linker_wert, relation, rechter_wert, nachfolger_id}` tuples

**Is there a default/else branch?**
Not automatically — but the handbook explicitly recommends creating a final catch-all rule (e.g., `1 = 1`) to prevent process abort when no condition matches.

**Full example DECISION action:**
```json
{
  "aktion_id": "step_decision_01",
  "aktionstyp": "DECISION",
  "parameter": {
    "verzweigungstyp": "Boolean",
    "regeln": [
      {
        "linker_wert": "{SR:step_find_01:Ausgeführt}",
        "relation": "=",
        "rechter_wert": "true",
        "nachfolger_id": "step_click_01"
      },
      {
        "linker_wert": "1",
        "relation": "=",
        "rechter_wert": "1",
        "nachfolger_id": "step_error_handler"
      }
    ]
  },
  "nachfolger": ["step_click_01", "step_error_handler"],
  "emma_kompatibel": false
}
```

---

## Cross-Cutting Section C: LOOP Iteration

**What does LOOP iterate over?**
LOOP is a **counter-controlled loop**, not a collection iterator. It increments an internal counter on each entry and exits when the counter reaches `maximale_anzahl_loops`. It does not natively iterate over a collection. Collection iteration is implemented by combining LOOP with IMPORT steps that read successive rows/columns using the loop counter as the row/column index.

**Which parameter specifies the collection/iteration variable?**
There is no native "collection" parameter. The loop counter is an implicit step result field, accessible as `{SR:loop_step_id:Ergebnisindex}` or used indirectly via variable manipulation to calculate the current Excel row/column index.

**Which parameter points to the first action inside the loop body?**
This is encoded in `nachfolger[0]` — the first element in the successor list. Per the handbook's branching semantics: `"Falsch"` (counter not yet at maximum) → routes to the step inside the loop body; `"Wahr"` (maximum reached) → routes to the step after the loop.

**Which parameter points to the action after the loop exits?**
`nachfolger[1]` — the second element in the successor list, taken when `"Wahr"` (max iterations reached).

**How is the loop variable referenced inside loop body actions?**
- The loop counter is available via the step's result fields (Ergebnisindex, Anzahl).
- Via variable manipulation: a variable can be set to the loop counter value, e.g., using "Wert zuweisen" from `{SR:loop_step:Ergebnisindex}`.
- The counter is then used in IMPORT/EXPORT `zeile` or `spalte` parameters to address the current row.

**Full example LOOP action:**
```json
{
  "aktion_id": "step_loop_01",
  "aktionstyp": "LOOP",
  "parameter": {
    "maximale_anzahl_loops": "100",
    "bei_max_zuruecksetzen": "false",
    "vor_start_zuruecksetzen": "true"
  },
  "nachfolger": ["step_loop_body_start", "step_after_loop"],
  "emma_kompatibel": false
}
```

---

## Cross-Cutting Section D: SUCCESS / Termination Semantics

**Does SUCCESS take parameters?**
No. The SUCCESS step has no parameters; its parameter dict is empty `{}`.

**Can there be multiple SUCCESS steps?**
Yes. The handbook states "Jeder Prozess benötigt einen Prozessschritt Erfolg" (each process needs a SUCCESS step), but does not restrict to exactly one. Multiple SUCCESS steps are used when a process has multiple valid termination paths (e.g., one per branch of a final DECISION).

**Does SUCCESS always appear as a leaf node?**
Yes. SUCCESS by definition ends the process; it has no `nachfolger` (empty list or `["END"]` sentinel).

**Is there a FAILURE or ERROR terminal action type?**
No. The handbook documents no dedicated FAILURE or ERROR terminal step type. Process failure is indicated at runtime by:
- A step being "nicht erfolgreich" without a fallback
- Reaching the end of a process without hitting a SUCCESS step (process is treated as "abgebrochen")
- Exception handling (Ausnahmebehandlung) is configured at the process level, not as a step type

The absence of an explicit FAILURE terminal is important: error paths typically route to SUCCESS (with a "failed" status logged separately) or fall off the graph (process abort).

---

## Cross-Cutting Section E: Action-Type-Specific Validation Rules

**Action types only valid in certain contexts:**
- NESTED_PROCESS: references a separate EMMA process by ID; the sub-process must exist and be loadable. Cannot be used to recursively call itself (would create infinite recursion).
- GENAI: requires EMMA Cortex add-on license; not available in base EMMA installation.

**Forbidden parameter combinations:**
- FIND: `objektnummer` without `gegenstand` in `{"Objekt","Bild"}` — the field is ignored but wastes configuration effort.
- FIND: `suchtext` + `gegenstand == "Objekt"` — mutually exclusive; text search fields are hidden in the UI when object is selected.
- CLICK: `nur_mouseover=True` together with `doppelklick=True` or `rechtsklick=True` — the latter two are silently ignored; should not be set.
- COMMAND: `capture_output != "No"` without `ende_abwarten=True` — output capture is silently skipped.
- WAIT: `meldung` with `gegenstand == "Zeit"` — message is not displayed for time-only wait.

**Error-prone parameter combinations:**
- LOOP: Missing catch-all DECISION rule before the loop body can cause the loop to be exited early via a non-matching DECISION, logging as "nicht erfolgreich".
- DECISION: No fallback rule — if no rule matches, the process aborts without reaching SUCCESS; always add a `1 = 1` fallback.
- FIND (Text/RegEx): Selecting wrong OCR profile (`"Tabelle"` or `"Tabelle erzwingen"`) for simple non-tabular text slows recognition significantly.
- NESTED_PROCESS: Mismatched variable interface settings (Eingehend/Ausgehend/Ein/Aus) silently prevents variable transfer.
- READ_FORM: Document rotated > 30° causes extraction failure without an obvious error.
- EXPORT/IMPORT: Excel `tabelle` parameter starts at 1 (not 0); off-by-one errors are common.

---

## Suggested Pydantic Union

### 1. All Parameter Model Classes

```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class FindParameter(BaseModel):
    gegenstand: Literal["Objekt", "Text", "RegEx", "Bild", "Sprachen", "Freeze"]
    quelldokument: Literal["Bildschirm", "Datei", "Ergebnisfeld"] = "Bildschirm"
    warte_vor_start_ms: int = 0
    timeout_ms: int | None = None
    objektnummer: str | None = None
    minimaler_score: float = 0.9
    suchtext: str | None = None
    gross_kleinschreibung: bool = False
    datei: str | None = None
    seiten: str | None = None
    reihenfolge: str = "Höchstes"
    treffer_nr: int = 1
    filter: str | None = None
    filter_koordinate: float | None = None
    ocr_profil: str = "Default"
    ocr_modus: str = "Default"
    mit_neuer_aufloesung: int | float = 2
    zoom: float = 1.0
    bildverbesserung: str = "Keine"
    kontrast_verbessern: bool = False
    text_rotation: str = "Aus"
    texttyp: str = "Default"
    sprachen: list[str] = []
    erweiterte_optionen: str | None = None


class FindAndClickParameter(FindParameter):
    pass


class ClickParameter(BaseModel):
    x: float
    y: float
    versatz_x: float = 0.0
    versatz_y: float = 0.0
    dauer_ms: int = 0
    doppelklick: bool = False
    rechtsklick: bool = False
    nur_mouseover: bool = False


class DragParameter(BaseModel):
    start_x: float
    start_y: float
    ende_x: float
    ende_y: float
    start_versatz_x: float = 0.0
    start_versatz_y: float = 0.0
    ende_versatz_x: float = 0.0
    ende_versatz_y: float = 0.0


class ScrollParameter(BaseModel):
    gegenstand: Literal["Klick", "Pixel"]
    richtung: Literal["Links", "Rechts", "Hoch", "Runter"]
    schritte: int
    warte_vor_start_ms: int = 0
    start_x: float | None = None
    start_y: float | None = None


class TypeParameter(BaseModel):
    eingabetext: str
    key_basiertes_tippen: bool = False
    text_unveraendert_eingeben: bool = False


class ReadParameter(BaseModel):
    gegenstand: Literal["Text", "Text-Field", "Objekt"]
    referenz_x: float
    referenz_y: float
    breite: float
    hoehe: float
    warte_vor_start_ms: int = 0
    timeout_ms: int | None = None
    versatz_x: float = 0.0
    versatz_y: float = 0.0
    in_zwischenablage: bool = False
    quelldokument: Literal["Bildschirm", "Datei"] = "Bildschirm"
    datei: str | None = None
    seite: int | None = None
    validierungsmuster: str | None = None
    ocr_profil: str = "Default"
    ocr_modus: str = "Default"
    mit_neuer_aufloesung: int | float = 2
    zoom: float = 1.0
    bildverbesserung: str = "Keine"
    kontrast_verbessern: bool = False
    text_rotation: str = "Aus"
    texttyp: str = "Default"
    sprachen: list[str] = []
    obere_tiefenschaerfe: int = 200
    untere_tiefenschaerfe: int = 50
    min_uebereinstimmung: float = 2.0


class ReadFormParameter(BaseModel):
    form_id: str
    input_file: str
    page_to_read: int = 1


class GenAIParameter(BaseModel):
    skill: str
    skill_inputs: dict[str, str] = {}
    save_to_csv: bool = False


class ExportParameter(BaseModel):
    datei: str
    spalte: str
    zeile: int
    wert: str
    gegenstand: str = "Zelle"
    tabelle: int = 1
    trennzeichen: str = ","
    erste_zeile_ignorieren: bool = False


class ImportParameter(BaseModel):
    gegenstand: Literal["Zelle", "Zeile", "Spalte", "Ganze Zeile", "Ganze Spalte"]
    datei: str
    spalte: str
    zeile: int
    tabelle: int = 1
    trennzeichen: str = ","
    erste_zeile_ignorieren: bool = False
    letzte_spalte: str | None = None
    letzte_zeile: int | None = None
    timeout_ms: int | None = None


class FileOperationParameter(BaseModel):
    gegenstand: Literal[
        "Datei Name", "Datei öffnen", "Datei kopieren", "Datei verschieben",
        "Datei löschen", "Verzeichnis Name", "Verzeichnis öffnen",
        "Verzeichnis verschieben", "Verzeichnis zippen"
    ]
    quelle: str
    dateiname: str
    sortierung: str | None = None
    position: int = 1
    ziel: str | None = None
    ueberschreiben: bool = False
    neuer_dateiname: str | None = None


class SendMailParameter(BaseModel):
    mail_an: str
    betreff: str
    mail_text: str
    cc: str | None = None
    bcc: str | None = None
    anhang: str | None = None


class CommandParameter(BaseModel):
    dateiname: str
    arbeitsverzeichnis: str | None = None
    argumente: str | None = None
    versteckt: bool = False
    ende_abwarten: bool = True
    capture_output: Literal["No", "Output", "Error", "Both"] = "No"


class LoopParameter(BaseModel):
    maximale_anzahl_loops: int
    bei_max_zuruecksetzen: bool = False
    vor_start_zuruecksetzen: bool = False


class DecisionRule(BaseModel):
    linker_wert: str
    relation: str
    rechter_wert: str
    nachfolger_id: str


class DecisionParameter(BaseModel):
    verzweigungstyp: Literal["Boolean", "Ganzzahl", "Dezimalzahl", "Text", "Datum&Uhrzeit"]
    regeln: list[DecisionRule]


class WaitParameter(BaseModel):
    gegenstand: Literal["Zeit", "Bestätigung", "Eingabe"]
    timeout_ms: int
    meldung: str | None = None


class SuccessParameter(BaseModel):
    pass


# NEW — not yet in enum
class NestedProcessParameter(BaseModel):
    prozess_id: int
    variablen: dict[str, str] = {}
```

### 2. Updated EmmaAktionstyp StrEnum

```python
from enum import StrEnum


class EmmaAktionstyp(StrEnum):
    # Original 18
    FIND = "FIND"
    FIND_AND_CLICK = "FIND_AND_CLICK"
    CLICK = "CLICK"
    DRAG = "DRAG"
    SCROLL = "SCROLL"
    TYPE = "TYPE"
    READ = "READ"
    READ_FORM = "READ_FORM"
    GENAI = "GENAI"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    FILE_OPERATION = "FILE_OPERATION"
    SEND_MAIL = "SEND_MAIL"
    COMMAND = "COMMAND"
    LOOP = "LOOP"
    DECISION = "DECISION"
    WAIT = "WAIT"
    SUCCESS = "SUCCESS"
    # NEW — found in handbook but not yet in original enum
    NESTED_PROCESS = "NESTED_PROCESS"  # Sub-process call
```

### 3. Union Type Replacing `parameter: dict[str, str]`

```python
from typing import Annotated, Union
from pydantic import Field


EmmaAktionParameter = Annotated[
    Union[
        FindParameter,
        FindAndClickParameter,
        ClickParameter,
        DragParameter,
        ScrollParameter,
        TypeParameter,
        ReadParameter,
        ReadFormParameter,
        GenAIParameter,
        ExportParameter,
        ImportParameter,
        FileOperationParameter,
        SendMailParameter,
        CommandParameter,
        LoopParameter,
        DecisionParameter,
        WaitParameter,
        SuccessParameter,
        NestedProcessParameter,
    ],
    Field(discriminator=None),  # No shared discriminator field; use model_validator below
]


class EmmaAktion(BaseModel):
    aktion_id: str
    aktionstyp: EmmaAktionstyp
    parameter: EmmaAktionParameter
    nachfolger: list[str]           # ["END"] signals termination
    emma_kompatibel: bool = False
    kompatibilitaets_hinweis: str | None = None

    @model_validator(mode="before")
    @classmethod
    def coerce_parameter_type(cls, values: dict) -> dict:
        """
        Disambiguate the parameter dict by aktionstyp before validation.
        This replaces the Union discriminator since parameter models do not
        share a common tag field.
        """
        typ = values.get("aktionstyp")
        raw = values.get("parameter", {})
        mapping: dict[str, type[BaseModel]] = {
            "FIND": FindParameter,
            "FIND_AND_CLICK": FindAndClickParameter,
            "CLICK": ClickParameter,
            "DRAG": DragParameter,
            "SCROLL": ScrollParameter,
            "TYPE": TypeParameter,
            "READ": ReadParameter,
            "READ_FORM": ReadFormParameter,
            "GENAI": GenAIParameter,
            "EXPORT": ExportParameter,
            "IMPORT": ImportParameter,
            "FILE_OPERATION": FileOperationParameter,
            "SEND_MAIL": SendMailParameter,
            "COMMAND": CommandParameter,
            "LOOP": LoopParameter,
            "DECISION": DecisionParameter,
            "WAIT": WaitParameter,
            "SUCCESS": SuccessParameter,
            "NESTED_PROCESS": NestedProcessParameter,
        }
        model_cls = mapping.get(str(typ))
        if model_cls and isinstance(raw, dict):
            values["parameter"] = model_cls.model_validate(raw)
        return values
```

> **Note on `discriminator`:** Because the parameter models do not share a common discriminator field (like `type`), a `model_validator` approach is used to select the correct model class by `aktionstyp`. An alternative is to add `aktionstyp: EmmaAktionstyp` as a field inside each parameter model (making it self-describing), which would enable Pydantic's built-in discriminated union — but that would be a more invasive schema change.
