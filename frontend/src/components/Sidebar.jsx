import { MessageSquare, Plus, Trash2 } from "lucide-react";
import UserProfile from "./UserProfile";

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  sidebarOpen
}) {
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
      </div>

      <div className="sidebar-footer">
        <UserProfile />
      </div>
    </div>
  );
}