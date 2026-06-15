import { useState, useEffect } from 'react'
import pdfService from '../services/pdfService'

export default function usePdf() {
  const [pdfStatus, setPdfStatus] = useState(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    let mounted = true
    const check = async () => {
      try {
        const data = await pdfService.getPdfStatus()
        if (!mounted) return
        if (data?.loaded) setPdfStatus(data)
        else setPdfStatus(null)
      } catch (err) {
        console.error('Could not fetch server PDF status:', err)
      }
    }
    check()
    return () => { mounted = false }
  }, [])

  return { pdfStatus, setPdfStatus, isUploading, setIsUploading }
}
