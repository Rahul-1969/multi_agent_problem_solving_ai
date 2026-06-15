import { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  return (
    <nav style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 40px",
      height: "68px",
      borderBottom: "1px solid var(--border-color)",
      background: "rgba(23, 23, 23, 0.95)",
      backdropFilter: "blur(12px)",
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      <Link to="/" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none", color: "var(--text-primary)" }}>
        <div style={{
          width: 34,
          height: 34,
          borderRadius: "10px",
          background: "linear-gradient(135deg, var(--accent-color), #8b5cf6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 16,
        }}>🧠</div>
        <span style={{ fontWeight: 700, fontSize: 17, letterSpacing: "-0.3px" }}>NeuralChat</span>
      </Link>

      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <Link to="/" style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 500 }}>
          Home
        </Link>
        <Link to="/about" style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 500 }}>
          About
        </Link>

        {user ? (
          <>
            <Link to="/chat" style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 500 }}>
              Dashboard
            </Link>
            <button
              onClick={logout}
              style={{
                padding: "8px 16px",
                borderRadius: "var(--radius-md)",
                background: "transparent",
                border: "1px solid var(--border-strong)",
                color: "var(--text-primary)",
                cursor: "pointer",
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: 14, fontWeight: 500 }}>
              Sign in
            </Link>
            <Link to="/register" style={{
              padding: "8px 16px",
              borderRadius: "var(--radius-md)",
              background: "var(--accent-color)",
              color: "#fff",
              textDecoration: "none",
              fontSize: 14,
              fontWeight: 600,
            }}>
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}