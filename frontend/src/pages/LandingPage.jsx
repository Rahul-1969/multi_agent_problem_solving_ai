import { Link } from 'react-router-dom'
import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'
import {
  Sparkles, ArrowRight, ChevronRight
} from 'lucide-react'

const FEATURES = [
  {
    icon: '🎓',
    color: 'rgba(74,222,128,0.12)',
    iconColor: 'var(--accent-college)',
    name: 'EAMCET College Predictor',
    desc: 'Get ranked predictions of safe, moderate, and dream colleges based on your rank, category, and branch preference.',
  },
  {
    icon: '💻',
    color: 'rgba(34,211,238,0.12)',
    iconColor: 'var(--accent-coding)',
    name: 'Coding Assistant',
    desc: 'Generate complete, production-quality code with syntax highlighting, time complexity analysis, and step-by-step explanations.',
  },
  {
    icon: '🩺',
    color: 'rgba(244,114,182,0.12)',
    iconColor: 'var(--accent-medical)',
    name: 'Medical Information',
    desc: 'Describe your symptoms for structured health information covering possible conditions, safe treatments, and lifestyle advice.',
  },
  {
    icon: '📖',
    color: 'rgba(251,146,60,0.12)',
    iconColor: 'var(--accent-edu)',
    name: 'Academic Study Aid',
    desc: 'Get definitions, key points, examples, and exam tips for CS subjects — from DBMS to Machine Learning.',
  },
  {
    icon: '📄',
    color: 'rgba(167,139,250,0.12)',
    iconColor: 'var(--accent-pdf)',
    name: 'PDF Question Answering',
    desc: 'Upload any PDF and ask questions about it. Perfect for research papers, textbooks, and study materials.',
  },
  {
    icon: '✨',
    color: 'rgba(99,102,241,0.12)',
    iconColor: 'var(--brand-from)',
    name: 'Smart Routing',
    desc: 'Queries are automatically classified and routed to the best-fit AI agent using a weighted keyword scoring system.',
  },
]

export default function LandingPage() {
  const { user } = useContext(AuthContext)

  return (
    <div className="landing-page">
      {/* Nav */}
      <nav className="landing-nav">
        <div className="landing-logo">
          <div className="landing-logo-icon">
            <Sparkles size={18} />
          </div>
          <span className="landing-logo-name">NeuralChat</span>
        </div>
        <div className="landing-nav-links">
          {user ? (
            <>
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                Hey, {user.name?.split(' ')?.[0] || 'there'}
              </span>
              <Link to="/chat" className="nav-btn-primary">
                Open Chat
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Sign in</Link>
              <Link to="/register" className="nav-btn-primary">
                Get Started
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">
          <Sparkles size={13} />
          Multi-Agent AI Assistant Platform
        </div>

        <h1 className="hero-title">
          One AI for every
          <br />
          <span className="grad">question you have</span>
        </h1>

        <p className="hero-desc">
          NeuralChat routes your queries to specialized AI agents — college prediction,
          medical info, coding help, academic study, and document Q&A. All in one place.
        </p>

        <div className="hero-actions">
          {user ? (
            <Link to="/chat" className="hero-btn-primary">
              Continue to Chat <ArrowRight size={16} />
            </Link>
          ) : (
            <>
              <Link to="/register" className="hero-btn-primary">
                Start for free <ArrowRight size={16} />
              </Link>
              <Link to="/login" className="hero-btn-secondary">
                Sign in
              </Link>
            </>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="section-label">What NeuralChat does</div>
        <h2 className="section-title">Six specialized agents, one interface</h2>

        <div className="feature-grid">
          {FEATURES.map((f, i) => (
            <div
              key={i}
              className="feature-card"
              style={{ animationDelay: `${i * 0.07}s` }}
            >
              <div
                className="feature-icon"
                style={{ background: f.color, color: f.iconColor }}
              >
                {f.icon}
              </div>
              <div className="feature-name">{f.name}</div>
              <div className="feature-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      {!user && (
        <section style={{ textAlign: 'center', padding: '64px 24px 80px' }}>
          <h2 style={{ fontSize: 30, fontWeight: 800, letterSpacing: -0.5, marginBottom: 12 }}>
            Ready to get started?
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, marginBottom: 28 }}>
            Create a free account and start chatting in seconds.
          </p>
          <Link to="/register" className="hero-btn-primary">
            Create free account <ChevronRight size={16} />
          </Link>
        </section>
      )}

      <footer className="landing-footer">
        © 2025 NeuralChat · Built with FastAPI & React · Powered by Ollama (phi3:mini)
      </footer>
    </div>
  )
}