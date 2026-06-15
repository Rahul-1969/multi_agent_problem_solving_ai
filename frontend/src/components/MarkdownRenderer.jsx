import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import { Copy, Check } from "lucide-react";

export default function MarkdownRenderer({ content }) {
  const [copiedCode, setCopiedCode] = useState(null);

  const copyToClipboard = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(index);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const components = {
    // Code block with syntax highlighting
    code({ inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || "");
      const language = match ? match[1] : "text";
      const codeString = String(children).replace(/\n$/, "");
      const codeIndex = `${language}-${codeString.slice(0, 20)}`;

      if (inline) {
        return (
          <code
            className="inline-code"
            style={{
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              padding: "2px 6px",
              borderRadius: "4px",
              fontFamily: "Consolas, monospace",
              fontSize: "0.9em",
              color: "#a3e7ff",
            }}
            {...props}
          >
            {children}
          </code>
        );
      }

      return (
        <div
          className="code-block-wrapper"
          style={{
            margin: "16px 0",
            borderRadius: "8px",
            overflow: "hidden",
            border: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          <div
            className="code-header"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "10px 16px",
              backgroundColor: "#1e1e2e",
              borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
            }}
          >
            <span
              style={{
                fontFamily: "Consolas, monospace",
                fontSize: "12px",
                color: "#8b95a7",
                fontWeight: "500",
              }}
            >
              {language.toUpperCase()}
            </span>
            <button
              onClick={() => copyToClipboard(codeString, codeIndex)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                backgroundColor: "rgba(255, 255, 255, 0.1)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                color: "#a3e7ff",
                padding: "6px 12px",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: "500",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = "rgba(163, 231, 255, 0.2)";
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
              }}
            >
              {copiedCode === codeIndex ? (
                <>
                  <Check size={14} />
                  Copied!
                </>
              ) : (
                <>
                  <Copy size={14} />
                  Copy
                </>
              )}
            </button>
          </div>
          <SyntaxHighlighter
            language={language}
            style={oneDark}
            customStyle={{
              margin: 0,
              padding: "16px",
              backgroundColor: "#0d1117",
              fontSize: "13px",
              lineHeight: "1.6",
            }}
          >
            {codeString}
          </SyntaxHighlighter>
        </div>
      );
    },

    // Headings
    h1({ children }) {
      return (
        <h1
          style={{
            fontSize: "28px",
            fontWeight: "700",
            marginTop: "20px",
            marginBottom: "12px",
            color: "var(--text-light)",
            lineHeight: "1.3",
          }}
        >
          {children}
        </h1>
      );
    },
    h2({ children }) {
      return (
        <h2
          style={{
            fontSize: "24px",
            fontWeight: "600",
            marginTop: "18px",
            marginBottom: "10px",
            color: "var(--text-light)",
            lineHeight: "1.3",
            borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
            paddingBottom: "8px",
          }}
        >
          {children}
        </h2>
      );
    },
    h3({ children }) {
      return (
        <h3
          style={{
            fontSize: "20px",
            fontWeight: "600",
            marginTop: "16px",
            marginBottom: "10px",
            color: "var(--text-light)",
          }}
        >
          {children}
        </h3>
      );
    },

    // Paragraphs
    p({ children }) {
      return (
        <p
          style={{
            fontSize: "15px",
            lineHeight: "1.6",
            marginBottom: "12px",
            color: "var(--text-primary)",
          }}
        >
          {children}
        </p>
      );
    },

    // Lists
    ul({ children }) {
      return (
        <ul
          style={{
            marginLeft: "20px",
            marginBottom: "12px",
            listStyle: "disc",
          }}
        >
          {children}
        </ul>
      );
    },
    ol({ children }) {
      return (
        <ol
          style={{
            marginLeft: "20px",
            marginBottom: "12px",
            listStyle: "decimal",
          }}
        >
          {children}
        </ol>
      );
    },
    li({ children }) {
      return (
        <li
          style={{
            marginBottom: "8px",
            fontSize: "15px",
            lineHeight: "1.6",
            color: "var(--text-primary)",
          }}
        >
          {children}
        </li>
      );
    },

    // Blockquote
    blockquote({ children }) {
      return (
        <blockquote
          style={{
            borderLeft: "4px solid var(--accent-color)",
            paddingLeft: "16px",
            marginLeft: "0",
            marginRight: "0",
            marginBottom: "12px",
            backgroundColor: "rgba(163, 231, 255, 0.1)",
            padding: "12px 16px",
            borderRadius: "4px",
            color: "var(--text-secondary)",
            fontStyle: "italic",
          }}
        >
          {children}
        </blockquote>
      );
    },

    // Table
    table({ children }) {
      return (
        <table
          style={{
            borderCollapse: "collapse",
            width: "100%",
            marginBottom: "16px",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          {children}
        </table>
      );
    },
    thead({ children }) {
      return (
        <thead
          style={{
            backgroundColor: "rgba(163, 231, 255, 0.1)",
            borderBottom: "2px solid rgba(255, 255, 255, 0.15)",
          }}
        >
          {children}
        </thead>
      );
    },
    tbody({ children }) {
      return <tbody>{children}</tbody>;
    },
    tr({ children }) {
      return (
        <tr style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.1)" }}>
          {children}
        </tr>
      );
    },
    td({ children }) {
      return (
        <td
          style={{
            padding: "12px 16px",
            textAlign: "left",
            fontSize: "14px",
            color: "var(--text-primary)",
          }}
        >
          {children}
        </td>
      );
    },
    th({ children }) {
      return (
        <th
          style={{
            padding: "12px 16px",
            textAlign: "left",
            fontSize: "14px",
            fontWeight: "600",
            color: "var(--text-light)",
          }}
        >
          {children}
        </th>
      );
    },

    // Strong and em
    strong({ children }) {
      return (
        <strong
          style={{
            fontWeight: "600",
            color: "var(--text-light)",
          }}
        >
          {children}
        </strong>
      );
    },
    em({ children }) {
      return (
        <em
          style={{
            fontStyle: "italic",
            color: "var(--text-secondary)",
          }}
        >
          {children}
        </em>
      );
    },

    // Links
    a({ href, children }) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: "var(--accent-color)",
            textDecoration: "none",
            borderBottom: "1px solid var(--accent-color)",
            cursor: "pointer",
            transition: "opacity 0.2s ease",
          }}
          onMouseEnter={(e) => (e.target.style.opacity = "0.8")}
          onMouseLeave={(e) => (e.target.style.opacity = "1")}
        >
          {children}
        </a>
      );
    },

    // Horizontal rule
    hr() {
      return (
        <hr
          style={{
            border: "none",
            borderTop: "1px solid rgba(255, 255, 255, 0.1)",
            margin: "20px 0",
          }}
        />
      );
    },
  };

  return (
    <div className="markdown-content">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
