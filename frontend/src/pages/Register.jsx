import { useState, useContext } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import authService from "../services/authService";
import { AuthContext } from "../context/AuthContext";

// Email validation regex
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Register() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) {
    return <Navigate to="/chat" replace />;
  }

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!name || !email || !password) {
      setError("Please fill in all fields");
      return;
    }

    if (!EMAIL_REGEX.test(email)) {
      setError("Please enter a valid email address");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (password.length > 72) {
      setError("Password must be at most 72 characters");
      return;
    }

    try {
      setLoading(true);
      await authService.register(name, email, password);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Unable to register user");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card animate-fade-up">
        <div className="auth-logo">🧠</div>
        <h2 className="auth-title">Create your account</h2>

        {error && (
          <div style={{
            color: "var(--accent-red)",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            padding: "10px",
            borderRadius: "var(--radius-sm)",
            fontSize: "13.5px",
            marginBottom: "16px",
            textAlign: "left",
            border: "1px solid rgba(239, 68, 68, 0.2)"
          }}>
            {error}
          </div>
        )}

        <form className="auth-form" onSubmit={handleRegister}>
          <div className="auth-input-group">
            <label className="auth-label" htmlFor="name">Full name</label>
            <input
              id="name"
              type="text"
              className="auth-input"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={loading}
              maxLength="100"
            />
          </div>

          <div className="auth-input-group">
            <label className="auth-label" htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              className="auth-input"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="auth-input-group">
            <label className="auth-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="auth-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              maxLength="72"
            />
            <small style={{ color: "var(--text-muted)", fontSize: "11px", marginTop: "4px" }}>
              6-72 characters
            </small>
          </div>

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? "Creating account..." : "Continue"}
          </button>
        </form>

        <p className="auth-footer-text">
          Already have an account?{" "}
          <Link to="/login" className="auth-link">
            Log in
          </Link>
        </p>

        <div style={{ marginTop: "20px" }}>
          <Link to="/" className="auth-link" style={{ fontSize: "13.5px", color: "var(--text-secondary)" }}>
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}