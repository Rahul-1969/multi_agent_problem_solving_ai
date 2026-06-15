import MarkdownRenderer from "./MarkdownRenderer";
import { Stethoscope, AlertCircle, Clock } from "lucide-react";

export default function MedicalResponse({ data }) {
  if (!data) return null;

  const {
    symptoms = "",
    possible_causes = [],
    recommendations = "",
    when_to_consult = "",
    disclaimer = "This is for informational purposes only. Please consult a healthcare professional for proper diagnosis.",
  } = data;

  return (
    <div className="structured-response medical-response">
      {/* Title */}
      <div className="response-title medical">
        <Stethoscope size={20} />
        <h1>Medical Assessment</h1>
      </div>

      {/* Symptoms */}
      {symptoms && (
        <div className="response-section">
          <h2>Symptoms Identified</h2>
          <MarkdownRenderer content={symptoms} />
        </div>
      )}

      {/* Possible Causes */}
      {possible_causes && possible_causes.length > 0 && (
        <div className="response-section">
          <h2>Possible Causes</h2>
          <ul className="causes-list">
            {possible_causes.map((cause, idx) => (
              <li key={idx}>
                <AlertCircle size={14} />
                {cause}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && (
        <div className="response-section">
          <h2>Recommendations</h2>
          <div className="recommendations-box">
            <MarkdownRenderer content={recommendations} />
          </div>
        </div>
      )}

      {/* When to Consult */}
      {when_to_consult && (
        <div className="response-section alert-section">
          <h2>
            <Clock size={16} />
            When to Consult a Doctor
          </h2>
          <div className="alert-box">
            <MarkdownRenderer content={when_to_consult} />
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="disclaimer">
        <AlertCircle size={16} />
        <p>{disclaimer}</p>
      </div>
    </div>
  );
}
