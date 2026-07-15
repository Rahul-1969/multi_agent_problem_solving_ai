import React, { useState } from 'react';
import { Bookmark, BookmarkCheck } from 'lucide-react';
import apiService from '../services/apiService';

export default function CareerTimeline({ roadmap }) {
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSavePlan = async () => {
    if (isSaving || isSaved) return;
    setIsSaving(true);
    try {
      await apiService.post('/api/v1/profile/career-plans', {
        career_goal: "Custom Career Plan",
        roadmap: roadmap
      });
      setIsSaved(true);
    } catch (err) {
      console.error("Failed to save career plan", err);
    } finally {
      setIsSaving(false);
    }
  };

  if (!roadmap || !roadmap.roadmap_steps || roadmap.roadmap_steps.length === 0) return null;

  return (
    <div className="career-timeline">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: "1rem 0" }}>
        <h3 style={{ margin: 0, color: "#1f2937" }}>Step-by-Step Timeline</h3>
        <button 
          onClick={handleSavePlan}
          disabled={isSaving || isSaved}
          style={{
            background: 'none', border: '1px solid #d1d5db', cursor: 'pointer',
            padding: '4px 10px', borderRadius: '4px',
            color: isSaved ? '#10b981' : '#4b5563',
            display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem'
          }}
        >
          {isSaved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
          {isSaved ? 'Saved' : (isSaving ? 'Saving...' : 'Save Plan')}
        </button>
      </div>
      <div style={{ position: "relative", borderLeft: "2px solid #3b82f6", marginLeft: "1rem", paddingLeft: "1.5rem" }}>
        {roadmap.roadmap_steps.map((step, idx) => (
          <div key={idx} style={{ marginBottom: "1.5rem", position: "relative" }}>
            <div style={{ position: "absolute", left: "-1.9rem", top: "0.2rem", width: "12px", height: "12px", borderRadius: "50%", background: "#3b82f6" }}></div>
            <h4 style={{ margin: "0 0 4px 0", color: "#1d4ed8" }}>{step.title} <span style={{ fontSize: "0.85rem", color: "#6b7280", fontWeight: "normal" }}>({step.estimated_duration})</span></h4>
            <p style={{ margin: "0 0 8px 0", fontSize: "0.95rem", color: "#4b5563" }}>{step.description}</p>
            
            {step.skills && step.skills.length > 0 && (
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "8px" }}>
                {step.skills.map((s, i) => (
                  <span key={i} style={{ background: "#e0f2fe", color: "#0369a1", padding: "2px 8px", borderRadius: "12px", fontSize: "0.8rem" }}>{s}</span>
                ))}
              </div>
            )}
            
            {step.milestone && (
              <div style={{ background: "#fef3c7", padding: "6px 10px", borderRadius: "4px", fontSize: "0.85rem", color: "#92400e", borderLeft: "3px solid #f59e0b" }}>
                <strong>Milestone:</strong> {step.milestone}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
