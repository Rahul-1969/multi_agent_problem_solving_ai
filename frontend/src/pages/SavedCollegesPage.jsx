import React, { useEffect, useState } from 'react';
import SavedCollegeFilters from '../components/SavedCollegeFilters';
import ExportButton from '../components/ExportButton';
import apiService from '../services/apiService';

export default function SavedCollegesPage() {
  const [colleges, setColleges] = useState([]);

  useEffect(() => {
    fetchColleges();
  }, []);

  const fetchColleges = async () => {
    try {
      const res = await apiService.get('/api/v1/profile/colleges');
      setColleges(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const removeCollege = async (code, branch) => {
    try {
      const res = await apiService.delete('/api/v1/profile/colleges', {
        data: { college_code: code, branch }
      });
      setColleges(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>Saved Colleges</h1>
        <ExportButton exportType="saved_colleges" title="Saved Colleges" data={{ colleges }} />
      </div>
      
      <SavedCollegeFilters onFilterChange={() => {}} />
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {colleges.map((c, idx) => (
          <div key={idx} style={{ padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
            <h3>{c.college_code}</h3>
            <p>Branch: {c.branch}</p>
            <p>Saved on: {new Date(c.saved_at).toLocaleDateString()}</p>
            <button onClick={() => removeCollege(c.college_code, c.branch)} style={{ color: 'red', marginTop: '8px' }}>Remove</button>
          </div>
        ))}
        {colleges.length === 0 && <p>No saved colleges yet.</p>}
      </div>
    </div>
  );
}
