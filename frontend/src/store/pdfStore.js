import create from 'zustand'
import pdfService from '../services/pdfService'

const usePdfStore = create((set) => ({
  pdfStatus: null,
  isUploading: false,

  setPdfStatus(status) {
    set({ pdfStatus: status })
  },

  setIsUploading(value) {
    set({ isUploading: value })
  },

  async fetchPdfStatus() {
    try {
      const data = await pdfService.getPdfStatus()
      set({ pdfStatus: data?.loaded ? data : null })
    } catch (error) {
      console.error('Failed to fetch PDF status:', error)
      set({ pdfStatus: null })
    }
  },

  async uploadPdf(file, sessionId = null) {
    set({ isUploading: true })
    try {
      const result = await pdfService.uploadPdf(file, sessionId)
      if (result?.success) {
        set({ pdfStatus: { ...result, loaded: true } })
      }
      return result
    } finally {
      set({ isUploading: false })
    }
  },

  async clearPdf(sessionId = null) {
    const result = await pdfService.clearPdf(sessionId)
    if (result?.success) {
      set({ pdfStatus: null })
    }
    return result
  },
}))

export default usePdfStore
