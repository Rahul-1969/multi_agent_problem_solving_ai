import React from 'react';
import useToastStore from '../store/toastStore';

export default function ToastContainer() {
  const toasts = useToastStore((state) => state.toasts);
  
  if (toasts.length === 0) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      {toasts.map((t) => (
        <div key={t.id} style={{
          padding: '12px 20px',
          borderRadius: '4px',
          color: '#fff',
          backgroundColor: 
            t.type === 'error' ? '#ef4444' : 
            t.type === 'warning' ? '#f59e0b' :
            t.type === 'info' ? '#3b82f6' :
            t.type === 'loading' ? '#6b7280' :
            '#10b981', // success
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          minWidth: '200px'
        }}>
          {t.message}
        </div>
      ))}
    </div>
  );
}
