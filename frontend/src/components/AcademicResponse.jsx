import MarkdownRenderer from "./MarkdownRenderer";
import { BookOpen, Lightbulb, Brain } from "lucide-react";

export default function AcademicResponse({ data }) {
  if (!data) return null;

  const {
    topic = "",
    definition = "",
    key_points = "",
    example = "",
    exam_tip = "",
    working = "",
    advantages = "",
    disadvantages = "",
    applications = "",
    summary = "",
  } = data;

  return (
    <div className="structured-response academic-response">
      {/* Title */}
      {topic && (
        <div className="response-title academic">
          <BookOpen size={20} />
          <h1>{topic}</h1>
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

      {/* Key Points */}
      {key_points && (
        <div className="response-section">
          <h2>Key Points</h2>
          <MarkdownRenderer content={key_points} />
        </div>
      )}

      {/* How It Works */}
      {working && (
        <div className="response-section">
          <h2>How It Works</h2>
          <MarkdownRenderer content={working} />
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

      {/* Advantages */}
      {advantages && (
        <div className="response-section">
          <h2>Advantages</h2>
          <MarkdownRenderer content={advantages} />
        </div>
      )}

      {/* Disadvantages */}
      {disadvantages && (
        <div className="response-section">
          <h2>Disadvantages</h2>
          <MarkdownRenderer content={disadvantages} />
        </div>
      )}

      {/* Applications */}
      {applications && (
        <div className="response-section">
          <h2>Applications</h2>
          <MarkdownRenderer content={applications} />
        </div>
      )}

      {/* Exam Tip */}
      {exam_tip && (
        <div className="response-section">
          <h2>
            <Lightbulb size={18} />
            Exam Tip
          </h2>
          <div className="tips-box">
            <MarkdownRenderer content={exam_tip} />
          </div>
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
