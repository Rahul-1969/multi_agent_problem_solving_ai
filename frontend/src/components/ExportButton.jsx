import React from 'react';
import useExport from '../hooks/useExport';

export default function ExportButton({ exportType, title, data, label = "Export PDF", format = "pdf" }) {
  const { exportData, isExporting } = useExport();

  const handleExport = async () => {
    await exportData(exportType, title, data, format);
  };

  return (
    <button 
      onClick={handleExport} 
      disabled={isExporting}
      style={{
        padding: '8px 16px',
        backgroundColor: '#4F46E5',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        cursor: isExporting ? 'not-allowed' : 'pointer',
        fontWeight: 'bold',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}
    >
      {isExporting ? (
        <span>Loading...</span>
      ) : (
        <>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          {label}
        </>
      )}
    </button>
  );
}
