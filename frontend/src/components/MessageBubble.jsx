import {
  Terminal, GraduationCap,
  Stethoscope, BookOpen, FileText, User, Cpu
} from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";
import CodingResponse from "./CodingResponse";
import MedicalResponse from "./MedicalResponse";
import AcademicResponse from "./AcademicResponse";

export default function MessageBubble({ sender, text, content, domain, data }) {
  const isUser = sender === "user";
  const displayText = text ?? content;


  // Render content based on domain & data structure
  const renderMessageContent = () => {
    if (isUser) {
      return (
        <div className="user-message-bubble">
          {displayText}
        </div>
      );
    }

    // Bot messages: check for structured data by domain
    if (domain === "coding" && data && typeof data === "object") {
      return <CodingResponse data={data} />;
    } else if (domain === "medical" && data && typeof data === "object") {
      return <MedicalResponse data={data} />;
    } else if (domain === "education" && data && typeof data === "object") {
      return <AcademicResponse data={data} />;
    } else if (domain === "college" && data) {
      return renderCollegeData(data);
    }

    // Fallback: render as markdown for general, pdf, or raw text responses
    return (
      <div className="bot-message-content">
        {domain && domain !== "general" && domain !== "user" && (
          <span className={`domain-badge ${domain}`}>
            {domain === "pdf" && <FileText size={12} style={{ marginRight: "4px" }} />}
            {domain === "coding" && <Terminal size={12} style={{ marginRight: "4px" }} />}
            {domain === "medical" && <Stethoscope size={12} style={{ marginRight: "4px" }} />}
            {domain === "education" && <BookOpen size={12} style={{ marginRight: "4px" }} />}
            {domain}
          </span>
        )}
        <MarkdownRenderer content={text} />
      </div>
    );
  };

  // College prediction rendering
  const renderCollegeData = (college) => {
    return (
      <div className="structured-response college-response">
        <div className="response-title college">
          <GraduationCap size={20} />
          <h1>College Prediction</h1>
        </div>

        {college.rank && (
          <div className="college-info-box">
            <div className="info-item">
              <span className="info-label">Rank:</span>
              <span className="info-value">{college.rank}</span>
            </div>
            {college.category && (
              <div className="info-item">
                <span className="info-label">Category:</span>
                <span className="info-value">{college.category}</span>
              </div>
            )}
            {college.gender && (
              <div className="info-item">
                <span className="info-label">Gender:</span>
                <span className="info-value">{college.gender}</span>
              </div>
            )}
            {college.branch && (
              <div className="info-item">
                <span className="info-label">Branch:</span>
                <span className="info-value">{college.branch}</span>
              </div>
            )}
          </div>
        )}

        {[
          { title: "Safe Options", key: "safe", color: "#10b981" },
          { title: "Moderate Options", key: "moderate", color: "#f59e0b" },
          { title: "Dream Options", key: "dream", color: "#8b5cf6" }
        ].map((tier) => {
          const list = college[tier.key] || [];
          if (list.length === 0) return null;

          return (
            <div key={tier.key} className="response-section">
              <h2 style={{ color: tier.color, display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{
                  display: "inline-block",
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  backgroundColor: tier.color,
                }}></span>
                {tier.title}
              </h2>
              <ul>
                {list.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={`message-row ${isUser ? "user-row" : "bot-row"}`}>
      {!isUser && (
        <div className="message-avatar-container bot" title="NeuralChat Bot">
          <Cpu size={16} />
        </div>
      )}
      <div className="message-content">
        {renderMessageContent()}
      </div>
      {isUser && (
        <div className="message-avatar-container user" title="You">
          <User size={16} />
        </div>
      )}
    </div>
  );
}