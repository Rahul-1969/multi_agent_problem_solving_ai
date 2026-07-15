import React from 'react';

export default function ResumeMatchScore({ score }) {
  let color = '#ef4444'; // Red for low score
  if (score >= 80) color = '#22c55e'; // Green
  else if (score >= 50) color = '#f59e0b'; // Yellow

  return (
    <div style={{ textAlign: 'center', margin: '20px 0' }}>
      <div 
        style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          border: `8px solid ${color}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto',
          fontSize: '32px',
          fontWeight: 'bold',
          color: color
        }}
      >
        {score}%
      </div>
      <h3 style={{ marginTop: '12px', color: '#374151' }}>Overall Match Score</h3>
    </div>
  );
}
