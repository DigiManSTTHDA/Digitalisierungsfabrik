/**
 * ChatPane — message list + text input (HLA 3.1).
 *
 * FR-A-01: Dialogischer Interviewprozess — user types, AI responds.
 * FR-F-03: No artifact data in the chat pane.
 * FR-A-08: UI labels in German.
 */

import { useEffect, useRef, useState } from "react";
import { useSession, useSessionDispatch } from "../store/session";
import { sendTurn } from "../api/websocket";

export function ChatPane() {
  const { chatMessages, isProcessing } = useSession();
  const dispatch = useSessionDispatch();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

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
        {chatMessages.length === 0 && (
          <p style={{ color: "#999", fontStyle: "italic" }}>
            Beschreiben Sie Ihren Geschäftsprozess...
          </p>
        )}
        {chatMessages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.text}
          </div>
        ))}
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
