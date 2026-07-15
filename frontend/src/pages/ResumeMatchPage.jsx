import React, { useState } from 'react';
import ResumeMatchScore from '../components/ResumeMatchScore';
import SkillGapCard from '../components/SkillGapCard';
import ExportButton from '../components/ExportButton';
import apiService from '../services/apiService';

export default function ResumeMatchPage() {
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleMatch = async (e) => {
    e.preventDefault();
    if (!file || !jdText) return alert("Upload resume and paste JD");
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('jd_text', jdText);

    try {
      const res = await apiService.post('/api/v1/resume/match', formData);
      const data = res.data;
      if (data.status === 'success') {
        setResult(data.data);
      } else {
        alert(data.message);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Resume vs Job Description Matching</h1>
      
      {!result ? (
        <form onSubmit={handleMatch} style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Upload Resume (PDF/DOCX)</label>
            <input type="file" accept=".pdf,.docx" onChange={e => setFile(e.target.files[0])} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Paste Job Description</label>
            <textarea 
              rows="10" 
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
              value={jdText}
              onChange={e => setJdText(e.target.value)}
            />
          </div>
          <button type="submit" disabled={loading} style={{ padding: '12px', backgroundColor: '#4f46e5', color: 'white', border: 'none', borderRadius: '4px' }}>
            {loading ? 'Analyzing...' : 'Match Resume'}
          </button>
        </form>
      ) : (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>Analysis Results</h2>
            <ExportButton exportType="resume_match" title="Resume Match Report" data={result} />
          </div>
          
          <ResumeMatchScore score={result.overall_match_score || 0} />
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            <div>
              <SkillGapCard 
                title="Skills Analysis" 
                matched={result.matched_skills} 
                missing={result.missing_skills} 
              />
              <SkillGapCard 
                title="Keywords Analysis" 
                matched={result.matched_keywords} 
                missing={result.missing_keywords} 
              />
            </div>
            <div>
              <h3>Gaps Identified</h3>
              <ul style={{ lineHeight: '1.6' }}>
                <li><strong>Experience:</strong> {result.experience_gap || 'No Gap'}</li>
                <li><strong>Education:</strong> {result.education_gap || 'No Gap'}</li>
                <li><strong>Certifications:</strong> {result.certification_gap || 'No Gap'}</li>
              </ul>
              
              {result.gemini_suggestions && (
                <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#eff6ff', borderRadius: '8px' }}>
                  <h3 style={{ color: '#1e40af', marginTop: 0 }}>AI Recommendations</h3>
                  <p style={{ color: '#1e3a8a' }}>{result.gemini_suggestions}</p>
                </div>
              )}
            </div>
          </div>
          
          <button onClick={() => setResult(null)} style={{ marginTop: '24px', padding: '8px 16px', cursor: 'pointer' }}>Start Over</button>
        </div>
      )}
    </div>
  );
}
