# CR-011: Init-Progress-Sichtbarkeit — UI-Feedback bei Background-Initialisierung tatsächlich sichtbar machen

| Feld | Wert |
|---|---|
| **ID** | CR-011 |
| **Titel** | Init-Progress-Sichtbarkeit — UI-Feedback bei Background-Initialisierung tatsächlich sichtbar machen |
| **Status** | Verifiziert |
| **Erstellt** | 2026-03-24 |
| **Priorität** | Hoch |
| **Auslöser** | CR-007 hat die Backend-Infrastruktur für Init-Progress-Events korrekt implementiert (Callback-Pattern, WebSocket-Event, Frontend-Store). Das UI-Rendering ist jedoch so implementiert, dass der User die Statusmeldungen faktisch nicht sieht: (1) Auto-Scroll reagiert nicht auf `initProgress`-Änderungen, (2) das Styling ist zu unauffällig (grauer kursiver Kleintext). Der Kernzweck von CR-007 — "der Nutzer sieht, dass das System arbeitet" — wird dadurch verfehlt. |
| **Abhängigkeiten** | Setzt voraus: CR-007 (Verifiziert) |

---

## 1. Problemstellung

### Kernproblem

Die Init-Progress-Meldungen (CR-007) werden technisch korrekt über WebSocket empfangen und im Session-Store gespeichert, aber der User sieht sie nicht. Die UI wirkt weiterhin eingefroren beim Phasenwechsel — genau der Zustand, den CR-007 beheben sollte.

### Konkrete Defizite

**D-1: Auto-Scroll ignoriert initProgress**

In `ChatPane.tsx:70-72` reagiert der `useEffect` für Auto-Scroll nur auf `chatMessages` und `validationReport`:

```tsx
useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [chatMessages, validationReport]);  // ← initProgress fehlt
```

Wenn `initProgress` sich ändert (z.B. von `null` auf `{status: "started", message: "Das System bereitet..."}`) wird das `<div>` zwar gerendert (Zeile 121-132), aber der Chat scrollt nicht nach unten. Der User sieht die letzte Chat-Nachricht und darunter — nichts. Die Init-Progress-Meldung ist außerhalb des sichtbaren Bereichs.

**D-2: Styling zu unauffällig**

Das Init-Progress-Element (`ChatPane.tsx:122-131`) hat:
- `color: #6b7280` (mittleres Grau — kaum Kontrast gegen weißen Hintergrund)
- `fontStyle: italic` (wirkt wie ein Hinweis, nicht wie ein aktiver Status)
- `fontSize: 0.85rem` (kleiner als reguläre Chat-Nachrichten)
- Kein Hintergrund, kein Icon, keine Animation

Selbst wenn der User zum Element scrollt, vermittelt das Styling nicht "System arbeitet gerade", sondern wirkt wie ein optionaler Hinweistext.

**D-3: Kein sofortiges Feedback nach Absenden**

Zwischen dem Absenden der Nachricht (`isProcessing = true`) und dem ersten `init_progress`-Event vergehen 5-15 Sekunden (Moderator-LLM-Call). In dieser Zeit zeigt der Senden-Button nur "..." — im Chat-Bereich selbst ist keine Aktivitätsanzeige sichtbar.

### Auswirkungen

- Der Kernzweck von CR-007 (User sieht, dass Init läuft) wird vollständig verfehlt
- User vermutet weiterhin Systemabsturz und bricht ab
- Die Backend-Infrastruktur (5 Callback-Stellen, Event-Serialisierung, WebSocket-Integration) bleibt wirkungslos

## 2. Ziel der Änderung

- Auto-Scroll reagiert auf `initProgress`-Änderungen → Init-Meldung ist immer im sichtbaren Bereich
- Init-Progress-Meldung hat auffälliges Styling mit visuellem Aktivitätsindikator (Puls-Animation), so dass der User sofort erkennt: "System arbeitet"
- Typing-Indicator (z.B. pulsierende Punkte) erscheint sofort wenn `isProcessing = true`, bevor das erste `init_progress`-Event eintrifft — überbrückt die 5-15 Sekunden Wartezeit
- Wenn `init_progress`-Events eintreffen, ersetzt die detaillierte Statusmeldung den generischen Typing-Indicator

## 3. Lösung

### 3.1 Fix Auto-Scroll Dependencies

In `ChatPane.tsx` den `useEffect` für Auto-Scroll um `initProgress` und `isProcessing` erweitern:

**IST** (Zeile 70-72):
```tsx
useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [chatMessages, validationReport]);
```

**SOLL**:
```tsx
useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [chatMessages, validationReport, initProgress, isProcessing]);
```

### 3.2 Typing-Indicator für sofortiges Feedback

Neues UI-Element im Chat-Bereich, das sofort erscheint wenn `isProcessing = true` und kein `initProgress` vorliegt:

**SOLL** (nach dem `initProgress`-Block, vor `<div ref={messagesEndRef} />`):
```tsx
{isProcessing && !initProgress && (
  <div className="typing-indicator">
    <span className="typing-dot" />
    <span className="typing-dot" />
    <span className="typing-dot" />
  </div>
)}
```

### 3.3 Init-Progress Styling aufwerten

Das bestehende `initProgress`-Element (`ChatPane.tsx:121-132`) erhält auffälligeres Styling:

**IST**:
```tsx
{initProgress && (
  <div
    style={{
      padding: "0.5rem 0.75rem",
      color: "#6b7280",
      fontStyle: "italic",
      fontSize: "0.85rem",
    }}
  >
    {initProgress.message}
  </div>
)}
```

**SOLL**:
```tsx
{initProgress && (
  <div className="init-progress">
    <span className="init-progress-dot" />
    {initProgress.message}
  </div>
)}
```

### 3.4 CSS-Klassen in App.css

Neue CSS-Klassen am Ende von `App.css`:

```css
/* Init Progress Indicator (CR-011) */
.init-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  background: #f0f4f8;
  border-radius: 6px;
  color: #475569;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.init-progress-dot {
  width: 8px;
  height: 8px;
  background: #2563eb;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

/* Typing Indicator (CR-011) */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0.6rem 0.75rem;
  margin-top: 0.25rem;
}

.typing-dot {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}
```

### 3.5 Abwärtskompatibilität

- Keine Änderungen am Backend, WebSocket-Protokoll oder Session-Store
- Keine neuen State-Felder — nutzt ausschließlich bestehendes `initProgress` und `isProcessing`
- Bestehende Inline-Styles werden durch CSS-Klassen ersetzt — funktional identisch, visuell aufgewertet
- Keine Breaking Changes

### 3.6 SDD-Konsistenz

**Konsistent.** FR-F-01 fordert: "Die aktuelle Systemphase und der Fortschritt innerhalb der Phase sind jederzeit sichtbar." Dieser CR stellt sicher, dass das Init-Progress-Feedback (bereits in CR-007 als Erweiterung von FR-F-01 definiert) tatsächlich sichtbar ist.

### 3.7 ADR-Konsistenz

- **ADR-008 (CR-006, Background-Init):** Nicht betroffen — rein Frontend-seitige Änderung, Init-Loop bleibt unverändert.
- **CR-007 Architektur (Callback-Pattern):** Nicht betroffen — die Event-Infrastruktur (Backend → WebSocket → Store) bleibt identisch. Nur die Rendering-Schicht wird angepasst.

---

### 3a. Abhängigkeiten & Konflikte

| Typ | CR | Beschreibung |
|---|---|---|
| Setzt voraus | CR-007 (Verifiziert) | Init-Progress-Events und Session-Store-Integration müssen existieren |
| Konflikt | — | Keine Konflikte mit bestehenden CRs. CR-010 (Debug-Logging) betrifft andere Dateien. |

---

## 4. Änderungsplan

### Phase 1: Auto-Scroll Fix

| # | Datei | Änderung |
|---|---|---|
| 1 | `frontend/src/components/ChatPane.tsx` | `useEffect`-Dependencies um `initProgress` und `isProcessing` erweitern (Zeile 72): `[chatMessages, validationReport, initProgress, isProcessing]` |

### Phase 2: Typing-Indicator

| # | Datei | Änderung |
|---|---|---|
| 2 | `frontend/src/components/ChatPane.tsx` | Nach dem `initProgress`-Block (Zeile 132) und vor `<div ref={messagesEndRef} />` (Zeile 133): Typing-Indicator-Element einfügen, sichtbar wenn `isProcessing && !initProgress` |

### Phase 3: Init-Progress Styling

| # | Datei | Änderung |
|---|---|---|
| 3 | `frontend/src/components/ChatPane.tsx` | Bestehendes `initProgress`-Element (Zeile 121-132) ersetzen: Inline-Styles durch CSS-Klasse `init-progress` ersetzen, pulsierenden Punkt (`init-progress-dot`) vor dem Text einfügen |
| 4 | `frontend/src/App.css` | Am Ende: CSS-Klassen `.init-progress`, `.init-progress-dot`, `.typing-indicator`, `.typing-dot` und `@keyframes pulse` hinzufügen (siehe Abschnitt 3.4) |

---

## 5. Risiken und Mitigationen

| # | Risiko | Mitigation |
|---|---|---|
| R-1 | Auto-Scroll triggert zu häufig (bei jedem `init_progress`-Event, d.h. pro Turn) | Akzeptabel — Scroll zum Ende ist immer korrekt wenn neue Inhalte erscheinen. `scrollIntoView({behavior: "smooth"})` ist idempotent und nicht störend. |
| R-2 | Typing-Indicator und Init-Progress überlappen bei Race Condition | Ausgeschlossen: Typing-Indicator wird nur bei `isProcessing && !initProgress` gezeigt. Sobald erstes `init_progress`-Event eintrifft, wird `initProgress` gesetzt → Typing-Indicator verschwindet, Init-Progress erscheint. |
| R-3 | CSS-Animation `pulse` kollidiert mit bestehendem CSS | `App.css` enthält keine `@keyframes pulse`-Definition — kein Namenskonflikt. |

---

## 6. Nicht im Scope

- Backend-Änderungen an der Init-Progress-Event-Infrastruktur (funktioniert korrekt)
- Session-Store-Änderungen (bestehende `SET_INIT_PROGRESS`-Action ist ausreichend)
- Cancel-Button zum Abbrechen der Init
- Fortschrittsbalken (Prozentanzeige) — die textuelle Meldung aus dem Event ist ausreichend
- Refactoring des Init-Progress-Elements in eine eigene Komponente

---

## 7. Abnahmekriterien

1. `useEffect`-Dependencies in `ChatPane.tsx` enthalten `initProgress` und `isProcessing`
2. Typing-Indicator (drei pulsierende Punkte) erscheint sofort wenn `isProcessing = true` und kein `initProgress` vorliegt
3. Typing-Indicator verschwindet wenn erstes `init_progress`-Event eintrifft
4. Init-Progress-Meldung hat sichtbaren Hintergrund (`#f0f4f8`), pulsierenden blauen Punkt und lesbare Schriftgröße (`0.9rem`)
5. Init-Progress-Element scrollt automatisch in den sichtbaren Bereich
6. CSS-Klassen `.init-progress`, `.init-progress-dot`, `.typing-indicator`, `.typing-dot` und `@keyframes pulse` existieren in `App.css`
7. Keine Inline-Styles mehr im Init-Progress-Element
8. Bestehende Chat-Funktionalität (Nachrichten senden/empfangen, Validation-Report) bleibt unverändert
9. Kein Breaking Change — Backend und Store bleiben unmodifiziert

---

## 8. Aufwandsschätzung

| Phase | Betroffene Dateien | Komplexität |
|---|---|---|
| Phase 1: Auto-Scroll Fix | `ChatPane.tsx` | S |
| Phase 2: Typing-Indicator | `ChatPane.tsx` | S |
| Phase 3: Init-Progress Styling | `ChatPane.tsx`, `App.css` | S |

| Aspekt | Wert |
|---|---|
| **Komplexität** | S (2 Dateien, kein Breaking Change, rein Frontend) |
| **Betroffene Dateien** | 2 (`frontend/src/components/ChatPane.tsx`, `frontend/src/App.css`) |
| **Breaking Change** | Nein |
