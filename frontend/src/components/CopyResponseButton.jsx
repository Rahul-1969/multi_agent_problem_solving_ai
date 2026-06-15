import { Copy, Check } from "lucide-react";
import { useState } from "react";

export default function CopyResponseButton({ text, label = "Copy Response" }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="copy-response-btn"
      title={label}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "6px",
        backgroundColor: "rgba(163, 231, 255, 0.15)",
        border: "1px solid rgba(163, 231, 255, 0.3)",
        color: "var(--accent-color)",
        padding: "8px 12px",
        borderRadius: "6px",
        cursor: "pointer",
        fontSize: "13px",
        fontWeight: "500",
        transition: "all 0.2s ease",
        marginTop: "12px",
      }}
      onMouseEnter={(e) => {
        e.target.style.backgroundColor = "rgba(163, 231, 255, 0.25)";
      }}
      onMouseLeave={(e) => {
        e.target.style.backgroundColor = "rgba(163, 231, 255, 0.15)";
      }}
    >
      {copied ? (
        <>
          <Check size={14} />
          Copied!
        </>
      ) : (
        <>
          <Copy size={14} />
          {label}
        </>
      )}
    </button>
  );
}
