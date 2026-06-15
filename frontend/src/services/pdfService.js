import apiService from './apiService'
import { PDF_ASK, PDF_LOAD, PDF_STATUS, PDF_UPLOAD, PDF_CLEAR } from '../constants/apiEndpoints'

const pdfService = {
  async getPdfStatus(sessionId = null) {
    const config = sessionId ? { params: { session_id: sessionId } } : undefined
    const response = await apiService.get(PDF_STATUS, config)
    return response.data
  },

  async askPdf(message, sessionId = null) {
    const payload = { message }
    if (sessionId) {
      payload.session_id = sessionId
    }
    const response = await apiService.post(PDF_ASK, payload)
    return response.data
  },

  async loadPdf(path, sessionId = null) {
    const payload = { path }
    if (sessionId) {
      payload.session_id = sessionId
    }
    const response = await apiService.post(PDF_LOAD, payload)
    return response.data
  },

  async uploadPdf(file, sessionId = null) {
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) {
      formData.append('session_id', sessionId)
    }
    const response = await apiService.post(PDF_UPLOAD, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async clearPdf(sessionId = null) {
    const config = sessionId ? { params: { session_id: sessionId } } : undefined
    const response = await apiService.delete(PDF_CLEAR, config)
    return response.data
  },
}

export default pdfService
