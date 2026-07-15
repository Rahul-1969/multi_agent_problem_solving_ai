import { useState } from 'react';
import useToastStore from '../store/toastStore';

export default function useExport() {
  const [isExporting, setIsExporting] = useState(false);
  const { success, error, loading, dismiss } = useToastStore();

  const exportData = async (exportType, title, data, format = 'pdf') => {
    const toastId = loading(`Generating ${format.toUpperCase()} export...`);
    setIsExporting(true);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/export/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          export_type: exportType,
          title: title,
          data: data
        })
      });

      if (!response.ok) {
        throw new Error('Export generation failed');
      }

      const result = await response.json();
      
      // Decode base64 and trigger download
      const binaryString = window.atob(result.base64_data);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      const blob = new Blob([bytes], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = result.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      dismiss(toastId);
      success(`${format.toUpperCase()} export successful!`);
    } catch (err) {
      console.error(err);
      dismiss(toastId);
      error(`Failed to generate ${format.toUpperCase()} export.`);
    } finally {
      setIsExporting(false);
    }
  };

  return { exportData, isExporting };
}
