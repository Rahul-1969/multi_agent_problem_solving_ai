import React from 'react';

export default function ScholarshipBookmarkCard({ scholarship, onRemove }) {
  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '20px',
      backgroundColor: '#ffffff',
      marginBottom: '16px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 style={{ margin: '0 0 8px 0', color: '#111827', fontSize: '20px' }}>
            {scholarship.scholarship_name}
          </h3>
          <p style={{ margin: '0 0 16px 0', color: '#6b7280', fontSize: '14px' }}>
            Provided by: {scholarship.provider}
          </p>
        </div>
        <div style={{
          backgroundColor: scholarship.match_score >= 80 ? '#dcfce7' : '#fef3c7',
          color: scholarship.match_score >= 80 ? '#166534' : '#92400e',
          padding: '4px 12px',
          borderRadius: '9999px',
          fontWeight: 'bold',
          fontSize: '14px'
        }}>
          {scholarship.match_score >= 80 ? 'Eligible' : 'Check Eligibility'}
        </div>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <div>
          <strong style={{ color: '#374151', fontSize: '14px' }}>Amount:</strong>
          <p style={{ margin: '4px 0 0 0', color: '#4b5563' }}>{scholarship.amount}</p>
        </div>
        <div>
          <strong style={{ color: '#374151', fontSize: '14px' }}>Deadline:</strong>
          <p style={{ margin: '4px 0 0 0', color: '#4b5563' }}>{scholarship.deadline}</p>
        </div>
      </div>
      
      <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '16px', display: 'flex', justifyContent: 'space-between' }}>
        {scholarship.official_link ? (
          <a href={scholarship.official_link} target="_blank" rel="noopener noreferrer" style={{ color: '#4f46e5', textDecoration: 'none', fontWeight: '500' }}>
            Visit Official Website &rarr;
          </a>
        ) : <span />}
        <button 
          onClick={onRemove}
          style={{
            backgroundColor: 'transparent',
            color: '#dc2626',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '500',
            fontSize: '14px'
          }}
        >
          Remove Bookmark
        </button>
      </div>
    </div>
  );
}
