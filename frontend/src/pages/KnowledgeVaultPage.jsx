import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../services/apiService'
import { ArrowLeft, Loader2, Trash2, UploadCloud, FileText } from 'lucide-react'
import './KnowledgeVaultPage.css'

const DOC_TYPE_OPTIONS = [
  'general',
  'syllabus',
  'placement',
  'college_faq',
  'resume',
  'scholarship',
  'interview_notes',
]

export default function KnowledgeVaultPage() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)

  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedFile, setSelectedFile] = useState(null)
  const [docType, setDocType] = useState('general')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')

  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    fetchDocuments()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      setError('')
      const res = await apiService.get('/api/v1/knowledge/list')
      setDocuments(res.data?.documents ?? [])
    } catch (err) {
      setError(err.message || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0] || null)
    setUploadError('')
    setUploadSuccess('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!selectedFile) {
      setUploadError('Please select a file to upload.')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('doc_type', docType)

    setUploading(true)
    setUploadError('')
    setUploadSuccess('')

    try {
      await apiService.post('/api/v1/knowledge/upload', formData)
      setUploadSuccess(`"${selectedFile.name}" uploaded successfully.`)
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setTimeout(() => setUploadSuccess(''), 4000)
      await fetchDocuments()
    } catch (err) {
      setUploadError(err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId, docName) => {
    setDeletingId(docId)
    try {
      await apiService.delete(`/api/v1/knowledge/${docId}`)
      setDocuments((prev) => prev.filter((d) => d.doc_id !== docId))
    } catch (err) {
      setError(err.message || `Failed to delete "${docName}". Please try again.`)
    } finally {
      setDeletingId(null)
    }
  }

  if (loading) {
    return (
      <div className="knowledge-vault-page">
        <div className="profile-edit-loading">
          <Loader2 className="profile-edit-spinner" size={32} />
          <p>Loading your knowledge vault...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="knowledge-vault-page">
      <div className="profile-edit-card">
        <button type="button" className="profile-edit-back" onClick={() => navigate(-1)}>
          <ArrowLeft size={18} />
          Back
        </button>

        <h1 className="profile-edit-title">Knowledge Vault</h1>
        <p className="profile-edit-subtitle">
          Upload documents to power your personalised AI answers. Supported: PDF, DOCX, TXT, MD.
        </p>

        {error && <div className="profile-edit-error">{error}</div>}

        <section className="profile-edit-section">
          <h2 className="profile-edit-section-title">Upload a document</h2>

          <form onSubmit={handleUpload} noValidate>
            {uploadError && <div className="profile-edit-error">{uploadError}</div>}
            {uploadSuccess && <div className="profile-edit-success">{uploadSuccess}</div>}

            <div className="profile-edit-field">
              <label htmlFor="kv-file-input" className="profile-edit-label">File</label>
              <input
                id="kv-file-input"
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt,.md"
                className="knowledge-vault-file-input"
                onChange={handleFileChange}
                disabled={uploading}
              />
              {selectedFile && (
                <p className="profile-edit-hint" style={{ marginTop: '6px' }}>
                  Selected: <strong>{selectedFile.name}</strong>
                </p>
              )}
            </div>

            <div className="profile-edit-field">
              <label htmlFor="kv-doc-type" className="profile-edit-label">Document type</label>
              <select
                id="kv-doc-type"
                className="profile-edit-select"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                disabled={uploading}
              >
                {DOC_TYPE_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            <div className="profile-edit-actions">
              <button
                type="submit"
                className="profile-edit-save"
                disabled={uploading || !selectedFile}
              >
                {uploading ? (
                  <>
                    <Loader2 className="profile-edit-spinner" size={16} />
                    Uploading...
                  </>
                ) : (
                  <>
                    <UploadCloud size={16} />
                    Upload
                  </>
                )}
              </button>
            </div>
          </form>
        </section>

        <section className="profile-edit-section">
          <h2 className="profile-edit-section-title">
            Your documents
            {documents.length > 0 && (
              <span className="knowledge-vault-count">{documents.length}</span>
            )}
          </h2>

          {documents.length === 0 ? (
            <div className="knowledge-vault-empty">
              <FileText size={40} strokeWidth={1.2} />
              <p>No documents yet. Upload one above to get started.</p>
            </div>
          ) : (
            <ul className="knowledge-vault-list">
              {documents.map((doc) => (
                <li key={doc.doc_id} className="knowledge-vault-item">
                  <div className="knowledge-vault-item-info">
                    <FileText size={18} className="knowledge-vault-item-icon" />
                    <div className="knowledge-vault-item-meta">
                      <span className="knowledge-vault-item-name">{doc.doc_name}</span>
                      <div className="knowledge-vault-item-badges">
                        <span className="knowledge-vault-badge">{doc.doc_type}</span>
                        {doc.chunk_count != null && (
                          <span className="knowledge-vault-badge knowledge-vault-badge-dim">
                            {doc.chunk_count} chunks
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="knowledge-vault-delete-btn"
                    onClick={() => handleDelete(doc.doc_id, doc.doc_name)}
                    disabled={deletingId === doc.doc_id}
                    aria-label={`Delete ${doc.doc_name}`}
                    title="Delete document"
                  >
                    {deletingId === doc.doc_id ? (
                      <Loader2 className="profile-edit-spinner" size={15} />
                    ) : (
                      <Trash2 size={15} />
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
