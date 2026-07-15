import React from 'react';

export default function SavedCollegeFilters({ onFilterChange }) {
  return (
    <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
      <input 
        type="text"
        placeholder="Search colleges..."
        onChange={(e) => onFilterChange({ search: e.target.value })}
        style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '4px', flex: 1 }}
      />
      <select 
        onChange={(e) => onFilterChange({ sort: e.target.value })}
        style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '4px' }}
      >
        <option value="name_asc">Name (A-Z)</option>
        <option value="name_desc">Name (Z-A)</option>
        <option value="rank">NIRF Rank</option>
      </select>
    </div>
  );
}
