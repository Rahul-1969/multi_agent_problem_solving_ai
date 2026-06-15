import { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { LogOut } from "lucide-react";

export default function UserProfile() {
  const { user, logout } = useContext(AuthContext);

  if (!user) {
    return (
      <div className="login-prompt-sidebar">
        <p>Chat history is disabled.</p>
        <Link to="/login" className="login-prompt-link">
          Sign in to save history
        </Link>
      </div>
    );
  }

  const firstLetter = user.name ? user.name.charAt(0).toUpperCase() : "?";

  return (
    <div className="user-profile-widget">
      <div className="user-info-section">
        <div className="avatar-circle">
          {firstLetter}
        </div>
        <div className="user-details">
          <span className="user-name">{user.name}</span>
          <span className="user-email">{user.email}</span>
        </div>
      </div>
      
      <button className="logout-btn" onClick={logout} title="Sign Out">
        <LogOut size={16} />
      </button>
    </div>
  );
}