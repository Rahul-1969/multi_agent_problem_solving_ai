import React from 'react';
import { Calendar, DollarSign, ExternalLink, Bookmark, BookmarkCheck } from 'lucide-react';
import apiService from '../services/apiService';
import MarkdownRenderer from './MarkdownRenderer';
import useToastStore from '../store/toastStore';

export default function ScholarshipCard({ scholarship }) {
  const [isSaved, setIsSaved] = React.useState(false);
  const [isSaving, setIsSaving] = React.useState(false);
  const { success, error } = useToastStore();

  const handleBookmark = async () => {
    if (isSaving || isSaved) return;
    setIsSaving(true);
    try {
      await apiService.post('/api/v1/profile/scholarships', {
        scholarship_id: scholarship.code || scholarship.scholarship_name,
      });
      setIsSaved(true);
      success('Scholarship bookmarked successfully');
    } catch (err) {
      console.error("Failed to bookmark scholarship", err);
      error('Failed to bookmark scholarship');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="metric-card" style={{ marginBottom: "1rem", display: "block" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <h3 style={{ margin: "0 0 8px 0", fontSize: "1.1rem", color: "#1f2937" }}>
          {scholarship.scholarship_name}
        </h3>
        <button 
          onClick={handleBookmark}
          disabled={isSaving || isSaved}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: isSaved ? '#10b981' : '#9ca3af',
            display: 'flex', alignItems: 'center'
          }}
          title="Save Scholarship"
        >
          {isSaved ? <BookmarkCheck size={20} /> : <Bookmark size={20} />}
        </button>
      </div>
      <p style={{ margin: "0 0 8px 0", color: "#4b5563", fontSize: "0.9rem" }}>
        <strong>Provider:</strong> {scholarship.provider}
      </p>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "8px" }}>
        <span style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.85rem", color: "#059669" }}>
          <DollarSign size={14} /> {scholarship.amount}
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.85rem", color: "#e11d48" }}>
          <Calendar size={14} /> {scholarship.deadline}
        </span>
      </div>
      
      <div style={{ padding: "10px", background: "#f3f4f6", borderRadius: "6px", fontSize: "0.9rem", color: "#374151" }}>
        <strong>Eligibility:</strong> {scholarship.eligibility}
      </div>
      
      {scholarship.summary && (
        <div style={{ marginTop: "10px", fontSize: "0.9rem" }}>
          <MarkdownRenderer content={scholarship.summary} />
        </div>
      )}
      
      {scholarship.official_link && (
        <div style={{ marginTop: "10px" }}>
          <a href={scholarship.official_link} target="_blank" rel="noreferrer" style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "#2563eb", textDecoration: "none", fontSize: "0.9rem", fontWeight: "500" }}>
            <ExternalLink size={14} /> Apply Here
          </a>
        </div>
      )}
    </div>
  );
}
