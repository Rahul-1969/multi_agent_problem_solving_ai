import { Routes, Route, Navigate } from 'react-router-dom'
import { useContext } from 'react'
import { AuthContext } from './context/AuthContext'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Register from './pages/Register'
import ChatPage from './pages/ChatPage'
import ComparePage from './pages/ComparePage'
import SavedCollegesPage from './pages/SavedCollegesPage'
import CareerPlansPage from './pages/CareerPlansPage'
import ResumeMatchPage from './pages/ResumeMatchPage'
import SavedScholarshipsPage from './pages/SavedScholarshipsPage'
import ProfileEditPage from './pages/ProfileEditPage'
import KnowledgeVaultPage from './pages/KnowledgeVaultPage'

function RequireAuth({ children }) {
  const { user, initializing } = useContext(AuthContext)
  if (initializing) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: 'var(--bg-void)'
      }}>
        <div className="loader-ring" />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/chat"
        element={
          <RequireAuth>
            <ChatPage />
          </RequireAuth>
        }
      />
      <Route
        path="/compare"
        element={
          <RequireAuth>
            <ComparePage />
          </RequireAuth>
        }
      />
      <Route
        path="/saved-colleges"
        element={
          <RequireAuth>
            <SavedCollegesPage />
          </RequireAuth>
        }
      />
      <Route
        path="/career-plans"
        element={
          <RequireAuth>
            <CareerPlansPage />
          </RequireAuth>
        }
      />
      <Route
        path="/resume-match"
        element={
          <RequireAuth>
            <ResumeMatchPage />
          </RequireAuth>
        }
      />
      <Route
        path="/saved-scholarships"
        element={
          <RequireAuth>
            <SavedScholarshipsPage />
          </RequireAuth>
        }
      />
      <Route
        path="/profile/edit"
        element={
          <RequireAuth>
            <ProfileEditPage />
          </RequireAuth>
        }
      />
      <Route
        path="/knowledge"
        element={
          <RequireAuth>
            <KnowledgeVaultPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}