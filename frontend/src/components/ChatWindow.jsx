import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import { Sparkles, Terminal, GraduationCap, Stethoscope, BookOpen } from "lucide-react";

export default function ChatWindow({ messages, isLoading, onSelectPrompt }) {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom on new messages or loading state change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const quickPrompts = [
    {
      title: "Predict EAMCET College",
      desc: "Check safe, moderate & dream colleges",
      prompt: "Predict college for rank 12000, category BC_B, gender female, branch CSE",
      icon: <GraduationCap size={16} style={{ color: "var(--accent-green)" }} />
    },
    {
      title: "Explain Coding Complexity",
      desc: "Analyze time/space of algorithms",
      prompt: "Write a merge sort algorithm in Python with time complexity and explanation",
      icon: <Terminal size={16} style={{ color: "var(--accent-purple)" }} />
    },
    {
      title: "Analyze Symptoms",
      desc: "Structured medical check & lifestyle tip",
      prompt: "I have a sore throat, runny nose and mild fatigue for 3 days",
      icon: <Stethoscope size={16} style={{ color: "var(--accent-red)" }} />
    },
    {
      title: "Academic Study Guide",
      desc: "Formulate definitions, examples & tips",
      prompt: "Explain Newton's Second Law of Motion with an example and exam tips",
      icon: <BookOpen size={16} style={{ color: "var(--accent-blue)" }} />
    }
  ];

  return (
    <div className="chat-scroll-area" ref={scrollRef}>
      <div className="chat-container-inner">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="welcome-logo">🧠</div>
            <h2 className="welcome-heading">What can I help with?</h2>
            
            <div className="prompts-grid">
              {quickPrompts.map((item, idx) => (
                <div 
                  key={idx} 
                  className="prompt-card"
                  onClick={() => onSelectPrompt(item.prompt)}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    {item.icon}
                    <div className="prompt-card-title">{item.title}</div>
                  </div>
                  <div className="prompt-card-desc">{item.desc}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble
              key={index}
              sender={msg.sender}
              text={msg.text}
              domain={msg.domain}
              data={msg.data}
            />
          ))
        )}

        {/* Loading / Typing indicator */}
        {isLoading && (
          <div className="message-row bot-row">
            <div className="message-avatar-container bot" title="NeuralChat Bot">
              <Sparkles size={14} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}