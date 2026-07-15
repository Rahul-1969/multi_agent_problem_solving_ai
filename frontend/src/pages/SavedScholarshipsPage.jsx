import React, { useEffect, useState } from 'react';
import ScholarshipBookmarkCard from '../components/ScholarshipBookmarkCard';
import ExportButton from '../components/ExportButton';
import useToastStore from '../store/toastStore';
import apiService from '../services/apiService';

export default function SavedScholarshipsPage() {
  const [scholarships, setScholarships] = useState([]);
  const { success, error } = useToastStore();

  useEffect(() => {
    fetchScholarships();
  }, []);

  const fetchScholarships = async () => {
    try {
      const res = await apiService.get('/api/v1/profile/scholarships');
      setScholarships(res.data.scholarships || []);
    } catch (err) {
      console.error(err);
    }
  };

  const removeBookmark = async (id) => {
    try {
      await apiService.delete('/api/v1/profile/scholarships', {
        data: { scholarship_id: id }
      });
      fetchScholarships(); // Reload to get fresh evaluated data
      success('Bookmark removed');
    } catch (err) {
      console.error(err);
      error('Failed to remove bookmark');
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>Bookmarked Scholarships</h1>
        <ExportButton exportType="scholarships" title="My Bookmarked Scholarships" data={{ scholarships }} />
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '20px' }}>
        {scholarships.map((s, idx) => (
          <ScholarshipBookmarkCard 
            key={idx}
            scholarship={s}
            onRemove={() => removeBookmark(s.code || s.scholarship_name)}
          />
        ))}
        {scholarships.length === 0 && <p>No bookmarked scholarships.</p>}
      </div>
    </div>
  );
}
