import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../services/apiService'
import { Loader2, X, ArrowLeft } from 'lucide-react'
import './ProfileEditPage.css'

const LANGUAGE_OPTIONS = ['English', 'Telugu', 'Hindi']
const MAX_WEAK_SUBJECTS = 10

const emptyProfile = {
  preferred_branch: '',
  preferred_location: '',
  preferred_colleges: [],
  career_goal: '',
  academic_year: '',
  category: '',
  gender: '',
  disability: false,
  income: '',
  state: '',
  weak_subjects: [],
  preferred_language: 'English',
}

export default function ProfileEditPage() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState(emptyProfile)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [tagError, setTagError] = useState('')

  useEffect(() => {
    fetchProfile()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      setError('')
      const res = await apiService.get('/api/v1/profile')
      setProfile((prev) => ({ ...prev, ...(res.data || {}) }))
    } catch (err) {
      setError(err.message || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }))
  }

  const canAddTag = (raw) => {
    const text = raw.trim()
    if (!text) return false
    if (profile.weak_subjects.includes(text)) return false
    if (profile.weak_subjects.length >= MAX_WEAK_SUBJECTS) return false
    return true
  }

  const addTag = (text = tagInput) => {
    const trimmed = text.trim()
    if (!trimmed) {
      setTagError('Enter a subject name before adding')
      return
    }
    if (profile.weak_subjects.length >= MAX_WEAK_SUBJECTS) {
      setTagError(`You can add at most ${MAX_WEAK_SUBJECTS} subjects`)
      return
    }
    if (profile.weak_subjects.includes(trimmed)) {
      setTagError('Subject already added')
      return
    }
    setProfile((prev) => ({ ...prev, weak_subjects: [...prev.weak_subjects, trimmed] }))
    setTagInput('')
    setTagError('')
  }

  const removeTag = (subject) => {
    setProfile((prev) => ({
      ...prev,
      weak_subjects: prev.weak_subjects.filter((s) => s !== subject),
    }))
    setTagError('')
  }

  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addTag()
    }
  }

  const isTagInputInvalid = tagInput.trim().length === 0 && tagInput.length > 0

  const buildPayload = () => ({
    ...profile,
    income: profile.income === '' ? null : Number(profile.income),
    weak_subjects: profile.weak_subjects || [],
    preferred_language: profile.preferred_language || 'English',
  })

  const isSaveDisabled = () => {
    if (saving || loading) return true
    if (isTagInputInvalid) return true
    if (tagInput.trim().length > 0 && !canAddTag(tagInput)) return true
    return false
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (isSaveDisabled()) return

    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const res = await apiService.post('/api/v1/profile', buildPayload())
      setProfile((prev) => ({ ...prev, ...(res.data || {}) }))
      setSuccess('Profile saved successfully')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="profile-edit-page">
        <div className="profile-edit-loading">
          <Loader2 className="profile-edit-spinner" size={32} />
          <p>Loading profile…</p>
        </div>
      </div>
    )
  }

  return (
    <div className="profile-edit-page">
      <div className="profile-edit-card">
        <button type="button" className="profile-edit-back" onClick={() => navigate(-1)}>
          <ArrowLeft size={18} />
          Back
        </button>

        <h1 className="profile-edit-title">Edit Profile</h1>
        <p className="profile-edit-subtitle">Update your preferences to get better recommendations</p>

        {error && <div className="profile-edit-error">{error}</div>}
        {success && <div className="profile-edit-success">{success}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <section className="profile-edit-section">
            <h2 className="profile-edit-section-title">Learning preferences</h2>

            <div className="profile-edit-field">
              <label htmlFor="weak-subjects-input" className="profile-edit-label">
                Topics I find difficult
              </label>
              <div className="profile-edit-tags">
                {profile.weak_subjects.map((subject) => (
                  <span key={subject} className="profile-edit-tag">
                    {subject}
                    <button
                      type="button"
                      className="profile-edit-tag-remove"
                      onClick={() => removeTag(subject)}
                      aria-label={`Remove ${subject}`}
                    >
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>

              <div className="profile-edit-tag-input-row">
                <input
                  id="weak-subjects-input"
                  type="text"
                  className={`profile-edit-input ${tagError || isTagInputInvalid ? 'profile-edit-input-error' : ''}`}
                  placeholder="e.g. DBMS"
                  value={tagInput}
                  onChange={(e) => {
                    setTagInput(e.target.value)
                    setTagError('')
                  }}
                  onKeyDown={handleTagKeyDown}
                  disabled={profile.weak_subjects.length >= MAX_WEAK_SUBJECTS}
                  maxLength={50}
                />
                <button
                  type="button"
                  className="profile-edit-tag-add"
                  onClick={() => addTag()}
                  disabled={!canAddTag(tagInput)}
                >
                  Add
                </button>
              </div>

              <div className="profile-edit-hint-row">
                {tagError ? (
                  <span className="profile-edit-field-error">{tagError}</span>
                ) : (
                  <span className="profile-edit-hint">
                    Press Enter or click Add. {profile.weak_subjects.length}/{MAX_WEAK_SUBJECTS} subjects.
                  </span>
                )}
              </div>
            </div>

            <div className="profile-edit-field">
              <label htmlFor="preferred-language" className="profile-edit-label">
                Preferred language for explanations
              </label>
              <select
                id="preferred-language"
                className="profile-edit-select"
                value={profile.preferred_language || 'English'}
                onChange={(e) => handleChange('preferred_language', e.target.value)}
              >
                {LANGUAGE_OPTIONS.map((lang) => (
                  <option key={lang} value={lang}>
                    {lang}
                  </option>
                ))}
              </select>
            </div>
          </section>

          <section className="profile-edit-section">
            <h2 className="profile-edit-section-title">General preferences</h2>

            <div className="profile-edit-grid">
              <div className="profile-edit-field">
                <label htmlFor="preferred-branch" className="profile-edit-label">Preferred branch</label>
                <input
                  id="preferred-branch"
                  type="text"
                  className="profile-edit-input"
                  value={profile.preferred_branch || ''}
                  onChange={(e) => handleChange('preferred_branch', e.target.value)}
                  placeholder="e.g. CSE"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="preferred-location" className="profile-edit-label">Preferred location</label>
                <input
                  id="preferred-location"
                  type="text"
                  className="profile-edit-input"
                  value={profile.preferred_location || ''}
                  onChange={(e) => handleChange('preferred_location', e.target.value)}
                  placeholder="e.g. Hyderabad"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="academic-year" className="profile-edit-label">Academic year / semester</label>
                <input
                  id="academic-year"
                  type="text"
                  className="profile-edit-input"
                  value={profile.academic_year || ''}
                  onChange={(e) => handleChange('academic_year', e.target.value)}
                  placeholder="e.g. 3rd year"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="career-goal" className="profile-edit-label">Career goal</label>
                <input
                  id="career-goal"
                  type="text"
                  className="profile-edit-input"
                  value={profile.career_goal || ''}
                  onChange={(e) => handleChange('career_goal', e.target.value)}
                  placeholder="e.g. Software Engineer"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="category" className="profile-edit-label">Category</label>
                <input
                  id="category"
                  type="text"
                  className="profile-edit-input"
                  value={profile.category || ''}
                  onChange={(e) => handleChange('category', e.target.value)}
                  placeholder="e.g. OC"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="gender" className="profile-edit-label">Gender</label>
                <input
                  id="gender"
                  type="text"
                  className="profile-edit-input"
                  value={profile.gender || ''}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  placeholder="e.g. Female"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="state" className="profile-edit-label">State</label>
                <input
                  id="state"
                  type="text"
                  className="profile-edit-input"
                  value={profile.state || ''}
                  onChange={(e) => handleChange('state', e.target.value)}
                  placeholder="e.g. Telangana"
                />
              </div>

              <div className="profile-edit-field">
                <label htmlFor="income" className="profile-edit-label">Annual income</label>
                <input
                  id="income"
                  type="number"
                  className="profile-edit-input"
                  value={profile.income || ''}
                  onChange={(e) => handleChange('income', e.target.value)}
                  placeholder="e.g. 500000"
                />
              </div>
            </div>

            <div className="profile-edit-field profile-edit-checkbox-field">
              <input
                id="disability"
                type="checkbox"
                className="profile-edit-checkbox"
                checked={!!profile.disability}
                onChange={(e) => handleChange('disability', e.target.checked)}
              />
              <label htmlFor="disability" className="profile-edit-label profile-edit-label-inline">
                Person with disability
              </label>
            </div>
          </section>

          <div className="profile-edit-actions">
            <button
              type="submit"
              className="profile-edit-save"
              disabled={isSaveDisabled()}
            >
              {saving ? (
                <>
                  <Loader2 className="profile-edit-spinner" size={16} />
                  Saving…
                </>
              ) : (
                'Save profile'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
