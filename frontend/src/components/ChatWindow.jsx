import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import { Terminal, GraduationCap, Stethoscope, BookOpen } from "lucide-react";

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

  const hasCollegeResponse = messages.some(msg => msg.domain === 'college');

  return (
    <div className="chat-scroll-area" ref={scrollRef}>
      <div className={`chat-container-inner ${hasCollegeResponse ? 'wide' : ''}`}>
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
          messages.map((msg, index) => {
            // Find the most recent user message before this bot message
            // so the copy button can format "prompt: ...\nresponse: ..."
            let prevUserText = null
            if (msg.sender !== 'user') {
              for (let i = index - 1; i >= 0; i--) {
                if (messages[i].sender === 'user') {
                  prevUserText = messages[i].text ?? messages[i].content ?? null
                  break
                }
              }
            }
            return (
              <MessageBubble
                key={msg.id || index}
                sender={msg.sender}
                text={msg.text ?? msg.content}
                content={msg.content}
                domain={msg.domain}
                data={msg.data}
                sources={msg.sources ?? null}
                used_rag={msg.used_rag ?? null}
                prevUserText={prevUserText}
              />
            )
          })
        )}
      </div>
    </div>
  );
}