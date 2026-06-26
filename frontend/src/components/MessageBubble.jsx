import {
  Terminal, GraduationCap,
  Stethoscope, BookOpen, FileText, User, Cpu, Sparkles
} from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";
import CodingResponse from "./CodingResponse";
import MedicalResponse from "./MedicalResponse";
import AcademicResponse from "./AcademicResponse";
import CollegeResponse from "./CollegeResponse";
import useChatStore from "../store/chatStore";

const DOMAIN_META = {
  education: { emoji: "🧠", label: "Education Pipeline" },
  coding: { emoji: "💻", label: "Coding Pipeline" },
  medical: { emoji: "🩺", label: "Medical Pipeline" },
  general: { emoji: "🌍", label: "General Pipeline" },
  college: { emoji: "🎓", label: "College Prediction" },
  pdf: { emoji: "📄", label: "PDF QA" },
};

export default function MessageBubble({ sender, text, content, domain, data }) {
  const isUser = sender === "user";
  const displayText = text ?? content;
  const currentDomain = useChatStore((state) => state.currentDomain) || "general";


  // Render content based on domain & data structure
  const renderMessageContent = () => {
    if (isUser) {
      return (
        <div className="user-message-bubble">
          {displayText}
        </div>
      );
    }

    // Loading bubble — pipeline-specific indicator
    if (domain === "loading") {
      const meta = DOMAIN_META[currentDomain] || DOMAIN_META.general;
      return (
        <div className="bot-message-content">
          <span className="domain-badge loading">
            <Sparkles size={12} style={{ marginRight: "4px" }} />
            {meta.emoji} {meta.label}
          </span>
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
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
      return <CollegeResponse data={data} />;
    }

    // Fallback: render as markdown for general, pdf, or raw text responses
    return (
      <div className="bot-message-content">
        {domain && domain !== "general" && domain !== "user" && domain !== "loading" && (
          <span className={`domain-badge ${domain}`}>
            {domain === "pdf" && <FileText size={12} style={{ marginRight: "4px" }} />}
            {domain === "coding" && <Terminal size={12} style={{ marginRight: "4px" }} />}
            {domain === "medical" && <Stethoscope size={12} style={{ marginRight: "4px" }} />}
            {domain === "education" && <BookOpen size={12} style={{ marginRight: "4px" }} />}
            {domain}
          </span>
        )}
        <MarkdownRenderer content={displayText} />
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