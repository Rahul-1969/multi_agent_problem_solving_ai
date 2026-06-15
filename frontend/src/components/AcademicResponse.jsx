import MarkdownRenderer from "./MarkdownRenderer";
import { BookOpen, CheckCircle, Lightbulb, Brain } from "lucide-react";

export default function AcademicResponse({ data }) {
  if (!data) return null;

  const {
    title = "",
    definition = "",
    explanation = "",
    example = "",
    diagram = "",
    key_formulas = [],
    tips = [],
    summary = "",
  } = data;

  return (
    <div className="structured-response academic-response">
      {/* Title */}
      {title && (
        <div className="response-title academic">
          <BookOpen size={20} />
          <h1>{title}</h1>
        </div>
      )}

      {/* Definition */}
      {definition && (
        <div className="response-section definition-section">
          <h2>Definition</h2>
          <div className="definition-box">
            <MarkdownRenderer content={definition} />
          </div>
        </div>
      )}

      {/* Explanation */}
      {explanation && (
        <div className="response-section">
          <h2>Detailed Explanation</h2>
          <MarkdownRenderer content={explanation} />
        </div>
      )}

      {/* Key Formulas */}
      {key_formulas && key_formulas.length > 0 && (
        <div className="response-section">
          <h2>Key Formulas</h2>
          <div className="formulas-grid">
            {key_formulas.map((formula, idx) => (
              <div key={idx} className="formula-card">
                <MarkdownRenderer content={formula} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Example */}
      {example && (
        <div className="response-section">
          <h2>Example</h2>
          <div className="example-box">
            <MarkdownRenderer content={example} />
          </div>
        </div>
      )}

      {/* Diagram */}
      {diagram && (
        <div className="response-section">
          <h2>Diagram</h2>
          <div className="diagram-box">
            <MarkdownRenderer content={diagram} />
          </div>
        </div>
      )}

      {/* Study Tips */}
      {tips && tips.length > 0 && (
        <div className="response-section">
          <h2>
            <Lightbulb size={18} />
            Study Tips
          </h2>
          <ul className="tips-list">
            {tips.map((tip, idx) => (
              <li key={idx}>
                <CheckCircle size={14} />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="response-section summary-section">
          <h2>
            <Brain size={18} />
            Summary
          </h2>
          <div className="summary-box">
            <MarkdownRenderer content={summary} />
          </div>
        </div>
      )}
    </div>
  );
}
