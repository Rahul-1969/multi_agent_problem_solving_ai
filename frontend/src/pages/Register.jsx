import { useState, useContext } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import authService from "../services/authService";
import { AuthContext } from "../context/AuthContext";
import { validateEmail, validatePassword, passwordsMatch } from "../utils/validation";
import { usePasswordToggle } from "../hooks/usePasswordToggle";
import AuthInput from "../components/auth/AuthInput";
import LoadingButton from "../components/auth/LoadingButton";
import SuccessOverlay from "../components/auth/SuccessOverlay";
import PasswordStrength from "../components/auth/PasswordStrength";
import { User, Mail, Lock } from "lucide-react";
import "./Auth.css";

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
  </svg>
);

const GitHubIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
  </svg>
);

const MicrosoftIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24">
    <rect x="1" y="1" width="10" height="10" fill="#F25022"/>
    <rect x="13" y="1" width="10" height="10" fill="#7FBA00"/>
    <rect x="1" y="13" width="10" height="10" fill="#00A4EF"/>
    <rect x="13" y="13" width="10" height="10" fill="#FFB900"/>
  </svg>
);

export default function Register() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const [pwdType, PwdIcon, togglePwd] = usePasswordToggle();
  const [confirmType, ConfirmIcon, toggleConfirm] = usePasswordToggle();

  if (user) return <Navigate to="/chat" replace />;

  const isEmailValid = email ? validateEmail(email) : null;
  const isNameValid = name.length > 1;
  const isPasswordValid = password ? validatePassword(password) : null;
  const isMatchValid = confirmPassword ? passwordsMatch(password, confirmPassword) : null;

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (!name || !email || !password || !confirmPassword) { setError("Please fill in all fields"); return; }
    if (isEmailValid === false) { setError("Please enter a valid email address"); return; }
    if (password.length < 8) { setError("Password must be at least 8 characters"); return; }
    if (isPasswordValid === false) { setError("Password must contain letters and numbers"); return; }
    if (password.length > 72) { setError("Password must be at most 72 characters"); return; }
    if (isMatchValid === false) { setError("Passwords do not match"); return; }

    try {
      setLoading(true);
      await authService.register(name, email, password);
      
      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Unable to create account");
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card animate-fade-up">
        <SuccessOverlay show={success} message="Account created!" />

        <div className="auth-logo-wrapper">
          <div className="auth-logo-icon">🧠</div>
        </div>

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Join NeuralChat and start your AI journey</p>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleRegister} noValidate>
          <AuthInput
            id="reg-name"
            label="Full name"
            icon={User}
            type="text"
            placeholder="Your Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="name"
            maxLength="100"
            disabled={loading || success}
            valid={name ? isNameValid : null}
          />

          <AuthInput
            id="reg-email"
            label="Email address"
            icon={Mail}
            type="email"
            placeholder="yourname@gmail.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            disabled={loading || success}
            valid={isEmailValid}
            error="Invalid email format"
          />

          <AuthInput
            id="reg-password"
            label="Password"
            icon={Lock}
            type={pwdType}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            maxLength="72"
            disabled={loading || success}
            valid={isPasswordValid}
            rightElement={
              <button
                type="button"
                className="auth-eye-btn"
                onClick={togglePwd}
                tabIndex={-1}
                disabled={loading || success}
                aria-label="Toggle password visibility"
              >
                <PwdIcon size={18} />
              </button>
            }
          />
          {password && <PasswordStrength password={password} />}

          <AuthInput
            id="reg-confirm"
            label="Confirm password"
            icon={Lock}
            type={confirmType}
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
            maxLength="72"
            disabled={loading || success}
            valid={isMatchValid}
            error="Passwords do not match"
            rightElement={
              isMatchValid ? null : (
                <button
                  type="button"
                  className="auth-eye-btn"
                  onClick={toggleConfirm}
                  tabIndex={-1}
                  disabled={loading || success}
                  aria-label="Toggle confirm password visibility"
                >
                  <ConfirmIcon size={18} />
                </button>
              )
            }
          />

          <LoadingButton type="submit" loading={loading} disabled={success}>
            Create account
          </LoadingButton>
        </form>

        <div className="auth-divider"><span>or continue with</span></div>
        <div className="auth-social">
          <button type="button" className="auth-social-btn" title="Google" disabled={loading || success}>
            <GoogleIcon /> Google
          </button>
          <button type="button" className="auth-social-btn" title="GitHub" disabled={loading || success}>
            <GitHubIcon /> GitHub
          </button>
          <button type="button" className="auth-social-btn" title="Microsoft" disabled={loading || success}>
            <MicrosoftIcon /> Microsoft
          </button>
        </div>

        <p className="auth-footer">
          Already have an account? <Link to="/login" className="auth-link">Login</Link>
        </p>
        <Link to="/" className="auth-back">← Back to home</Link>
      </div>
    </div>
  );
}