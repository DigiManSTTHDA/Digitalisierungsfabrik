/**
 * ChatPane — message list + text input (HLA 3.1).
 *
 * FR-A-01: Dialogischer Interviewprozess — user types, AI responds.
 * FR-F-03: No artifact data in the chat pane.
 * FR-A-08: UI labels in German.
 * FR-C-08: Validation findings rendered with severity badges.
 */

import { useEffect, useRef, useState } from "react";
import { useSession, useSessionDispatch } from "../store/session";
import { sendTurn } from "../api/websocket";
import type { components } from "../generated/api";

type ValidationBefund = components["schemas"]["ValidationBefundResponse"];

const SEVERITY_STYLES: Record<
  string,
  { color: string; bg: string; label: string }
> = {
  kritisch: { color: "#991b1b", bg: "#fef2f2", label: "Kritisch" },
  warnung: { color: "#92400e", bg: "#fffbeb", label: "Warnung" },
  hinweis: { color: "#1e40af", bg: "#eff6ff", label: "Hinweis" },
};

function ValidationBefundCard({ befund }: { befund: ValidationBefund }) {
  const style = SEVERITY_STYLES[befund.schweregrad] ?? SEVERITY_STYLES.hinweis;
  return (
    <div
      style={{
        padding: "0.4rem 0.6rem",
        marginBottom: "0.3rem",
        backgroundColor: style.bg,
        borderLeft: `3px solid ${style.color}`,
        borderRadius: "3px",
        fontSize: "0.85rem",
      }}
    >
      <span
        style={{
          fontSize: "0.7rem",
          fontWeight: 600,
          color: style.color,
          textTransform: "uppercase",
          marginRight: "0.4rem",
        }}
      >
        {style.label}
      </span>
      <span>{befund.beschreibung}</span>
      {befund.empfehlung && (
        <div
          style={{ fontSize: "0.75rem", color: "#6b7280", marginTop: "0.2rem" }}
        >
          Empfehlung: {befund.empfehlung}
        </div>
      )}
    </div>
  );
}

export function ChatPane() {
  const { chatMessages, isProcessing, validationReport, initProgress } =
    useSession();
  const dispatch = useSessionDispatch();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, validationReport]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || isProcessing) return;

    dispatch({
      type: "ADD_CHAT_MESSAGE",
      message: { role: "user", text },
    });
    dispatch({ type: "SET_PROCESSING", value: true });
    sendTurn(text);
    setInput("");
  };

  return (
    <div
      className="chat-pane"
      style={{ display: "flex", flexDirection: "column" }}
    >
      <div className="message-list" style={{ flex: 1, overflowY: "auto" }}>
        {chatMessages.length === 0 && !validationReport && (
          <p style={{ color: "#999", fontStyle: "italic" }}>
            Beschreiben Sie Ihren Geschäftsprozess...
          </p>
        )}
        {chatMessages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {validationReport && (
          <div style={{ marginTop: "0.5rem" }}>
            <div
              style={{
                fontWeight: 600,
                fontSize: "0.9rem",
                marginBottom: "0.3rem",
                color: validationReport.ist_bestanden ? "#166534" : "#991b1b",
              }}
            >
              Validierung (Durchlauf {validationReport.durchlauf_nr}):{" "}
              {validationReport.ist_bestanden ? "Bestanden" : "Nicht bestanden"}
            </div>
            {validationReport.befunde.map((b) => (
              <ValidationBefundCard key={b.befund_id} befund={b} />
            ))}
          </div>
        )}
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
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Nachricht eingeben..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={isProcessing}
        />
        <button onClick={handleSend} disabled={isProcessing || !input.trim()}>
          {isProcessing ? "..." : "Senden"}
        </button>
      </div>
    </div>
  );
}
