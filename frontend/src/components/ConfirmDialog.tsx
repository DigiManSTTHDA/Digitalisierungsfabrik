/**
 * ConfirmDialog — reusable confirmation modal (Epic 08-07).
 *
 * Used for destructive actions like project deletion.
 * Renders a modal overlay with title, message, confirm ("Löschen"),
 * and cancel ("Abbrechen") buttons.
 */

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  open,
  title,
  message,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div
      className="confirm-overlay"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={onCancel}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: "8px",
          padding: "1.5rem",
          maxWidth: "400px",
          width: "90%",
          boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ margin: "0 0 0.5rem 0" }}>{title}</h3>
        <p style={{ color: "#555", margin: "0 0 1.5rem 0" }}>{message}</p>
        <div
          style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}
        >
          <button
            onClick={onCancel}
            style={{
              padding: "0.4rem 1rem",
              border: "1px solid #d1d5db",
              borderRadius: "4px",
              background: "#fff",
              cursor: "pointer",
            }}
          >
            Abbrechen
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: "0.4rem 1rem",
              border: "none",
              borderRadius: "4px",
              background: "#dc2626",
              color: "#fff",
              cursor: "pointer",
            }}
          >
            Löschen
          </button>
        </div>
      </div>
    </div>
  );
}
