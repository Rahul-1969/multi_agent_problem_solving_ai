import { MessageSquare, Plus, Trash2, GraduationCap, Map, FileText, Award } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import UserProfile from "./UserProfile";

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  sidebarOpen
}) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className={`sidebar ${sidebarOpen ? "" : "sidebar-hidden"}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <Plus size={16} />
          New chat
        </button>
      </div>

      <div className="chat-list">
        <div className="chat-list-section-title">Recent Chats</div>
        {chats.length === 0 ? (
          <div style={{ padding: "12px", fontSize: "13px", color: "var(--text-muted)", textAlign: "center" }}>
            No chat history
          </div>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${chat.id === activeChatId ? "active" : ""}`}
              onClick={() => onSelectChat(chat.id)}
            >
              <MessageSquare size={15} style={{ marginRight: "10px", flexShrink: 0, color: "var(--text-secondary)" }} />
              <div className="chat-item-text">{chat.title || "New Chat"}</div>
              <button
                className="chat-delete-btn"
                onClick={(e) => {
                  e.stopPropagation(); // prevent selecting the chat when clicking delete
                  onDeleteChat(chat.id);
                }}
                title="Delete chat"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}

        <div className="chat-list-section-title" style={{ marginTop: "24px" }}>Apps & Tools</div>
        
        <div
          className={`chat-item ${location.pathname === "/saved-colleges" ? "active" : ""}`}
          onClick={() => navigate("/saved-colleges")}
        >
          <GraduationCap size={15} style={{ marginRight: "10px", flexShrink: 0, color: "var(--text-secondary)" }} />
          <div className="chat-item-text">Saved Colleges</div>
        </div>

        <div
          className={`chat-item ${location.pathname === "/career-plans" ? "active" : ""}`}
          onClick={() => navigate("/career-plans")}
        >
          <Map size={15} style={{ marginRight: "10px", flexShrink: 0, color: "var(--text-secondary)" }} />
          <div className="chat-item-text">Career Plans</div>
        </div>

        <div
          className={`chat-item ${location.pathname === "/resume-match" ? "active" : ""}`}
          onClick={() => navigate("/resume-match")}
        >
          <FileText size={15} style={{ marginRight: "10px", flexShrink: 0, color: "var(--text-secondary)" }} />
          <div className="chat-item-text">Resume Match</div>
        </div>

        <div
          className={`chat-item ${location.pathname === "/saved-scholarships" ? "active" : ""}`}
          onClick={() => navigate("/saved-scholarships")}
        >
          <Award size={15} style={{ marginRight: "10px", flexShrink: 0, color: "var(--text-secondary)" }} />
          <div className="chat-item-text">Saved Scholarships</div>
        </div>
      </div>

      <div className="sidebar-footer">
        <UserProfile />
      </div>
    </div>
  );
}