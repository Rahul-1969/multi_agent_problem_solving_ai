import React from 'react';

export default function SkillGapCard({ title, matched, missing }) {
  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '16px',
      backgroundColor: '#f9fafb',
      marginBottom: '16px'
    }}>
      <h4 style={{ margin: '0 0 12px 0', color: '#111827', fontSize: '18px' }}>{title}</h4>
      
      <div style={{ display: 'flex', gap: '24px' }}>
        <div style={{ flex: 1 }}>
          <h5 style={{ color: '#059669', marginBottom: '8px' }}>Matched</h5>
          {matched && matched.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#374151' }}>
              {matched.map((item, idx) => <li key={idx}>{item}</li>)}
            </ul>
          ) : (
            <p style={{ margin: 0, color: '#6b7280', fontStyle: 'italic' }}>None</p>
          )}
        </div>
        
        <div style={{ flex: 1 }}>
          <h5 style={{ color: '#dc2626', marginBottom: '8px' }}>Missing</h5>
          {missing && missing.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#374151' }}>
              {missing.map((item, idx) => <li key={idx}>{item}</li>)}
            </ul>
          ) : (
            <p style={{ margin: 0, color: '#6b7280', fontStyle: 'italic' }}>None</p>
          )}
        </div>
      </div>
    </div>
  );
}
