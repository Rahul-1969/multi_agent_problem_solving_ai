import MarkdownRenderer from "./MarkdownRenderer";
import { Terminal, CheckCircle, Clock, HardDrive } from "lucide-react";

export default function CodingResponse({ data }) {
  if (!data) return null;

  const {
    code = "",
    language = "code",
    explanation = "",
    output = "",
    time_complexity = "",
    space_complexity = "",
    key_points = [],
    title = "",
  } = data;

  return (
    <div className="structured-response coding-response">
      {/* Title */}
      {title && (
        <div className="response-title">
          <Terminal size={20} />
          <h1>{title}</h1>
        </div>
      )}

      {/* Explanation */}
      {explanation && (
        <div className="response-section">
          <h2>Explanation</h2>
          <MarkdownRenderer content={explanation} />
        </div>
      )}

      {/* Code */}
      {code && (
        <div className="response-section">
          <h2>Code</h2>
          <MarkdownRenderer
            content={`\`\`\`${language}\n${code}\n\`\`\``}
          />
        </div>
      )}

      {/* Complexity Info */}
      {(time_complexity || space_complexity) && (
        <div className="response-section">
          <h2>Complexity Analysis</h2>
          <div className="complexity-grid">
            {time_complexity && (
              <div className="complexity-item">
                <div className="complexity-label">
                  <Clock size={16} />
                  Time Complexity
                </div>
                <div className="complexity-value">{time_complexity}</div>
              </div>
            )}
            {space_complexity && (
              <div className="complexity-item">
                <div className="complexity-label">
                  <HardDrive size={16} />
                  Space Complexity
                </div>
                <div className="complexity-value">{space_complexity}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Output */}
      {output && (
        <div className="response-section">
          <h2>Expected Output</h2>
          <MarkdownRenderer content={`\`\`\`\n${output}\n\`\`\``} />
        </div>
      )}

      {/* Key Points */}
      {key_points && key_points.length > 0 && (
        <div className="response-section">
          <h2>Key Points</h2>
          <ul>
            {key_points.map((point, idx) => (
              <li key={idx}>
                <CheckCircle size={14} />
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
