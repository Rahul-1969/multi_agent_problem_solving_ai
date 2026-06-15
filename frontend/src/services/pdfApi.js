import API from './api'

export async function getPdfStatus() {
  return API.get('/pdf/status')
}

export async function askPdf(message) {
  return API.post('/pdf/ask', { message })
}

export async function uploadPdf(formData) {
  return API.post('/pdf/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export async function loadPdfByPath(path) {
  return API.post('/pdf/load', { path })
}

export async function clearPdf() {
  return API.post('/pdf/clear')
}
