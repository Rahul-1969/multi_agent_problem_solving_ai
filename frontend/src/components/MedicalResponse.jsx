import MarkdownRenderer from "./MarkdownRenderer";
import { Stethoscope, AlertCircle } from "lucide-react";

export default function MedicalResponse({ data }) {
  if (!data) return null;

  const {
    conditions = "",
    treatments = "",
    lifestyle = "",
    emergency = "",
    disclaimer = "This is for informational purposes only. Please consult a healthcare professional for proper diagnosis.",
  } = data;

  return (
    <div className="structured-response medical-response">
      {/* Title */}
      <div className="response-title medical">
        <Stethoscope size={20} />
        <h1>Medical Assessment</h1>
      </div>

      {/* Conditions */}
      {conditions && (
        <div className="response-section">
          <h2>Possible Conditions</h2>
          <MarkdownRenderer content={conditions} />
        </div>
      )}

      {/* Treatments */}
      {treatments && (
        <div className="response-section">
          <h2>Safe Treatments</h2>
          <div className="recommendations-box">
            <MarkdownRenderer content={treatments} />
          </div>
        </div>
      )}

      {/* Lifestyle */}
      {lifestyle && (
        <div className="response-section">
          <h2>Lifestyle & Precautions</h2>
          <MarkdownRenderer content={lifestyle} />
        </div>
      )}

      {/* Emergency */}
      {emergency && (
        <div className="response-section alert-section">
          <h2>
            <AlertCircle size={16} />
            Seek Immediate Help If
          </h2>
          <div className="alert-box">
            <MarkdownRenderer content={emergency} />
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
