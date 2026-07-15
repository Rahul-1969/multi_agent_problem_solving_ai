import React from 'react';
import { AlertTriangle, Lightbulb, CheckCircle } from 'lucide-react';

export default function ResumeScore({ data }) {
  if (!data) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Extracted Information */}
      <div className="metric-card" style={{ display: "block" }}>
        <h3 style={{ margin: "0 0 12px 0", fontSize: "1rem", color: "#1f2937", borderBottom: "1px solid #e5e7eb", paddingBottom: "4px" }}>
          Extracted Data
        </h3>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", marginBottom: "8px" }}>
          <span style={{ fontSize: "0.85rem", color: "#4b5563" }}>
            <strong>Skills:</strong> {data.detected_skills?.length || 0} found
          </span>
          <span style={{ fontSize: "0.85rem", color: "#4b5563" }}>
            <strong>Experience:</strong> {data.experience?.length || 0} roles
          </span>
          <span style={{ fontSize: "0.85rem", color: "#4b5563" }}>
            <strong>Education:</strong> {data.education?.length || 0} entries
          </span>
        </div>
        {data.resume_summary && (
          <p style={{ fontSize: "0.85rem", color: "#374151", margin: "8px 0 0 0", fontStyle: "italic" }}>
            "{data.resume_summary.substring(0, 150)}{data.resume_summary.length > 150 ? '...' : ''}"
          </p>
        )}
      </div>

      {/* Missing Elements / Structural Flaws */}
      {data.missing_skills && data.missing_skills.length > 0 && (
        <div className="metric-card" style={{ display: "block", background: "#fef2f2", border: "1px solid #fecaca" }}>
          <h3 style={{ margin: "0 0 8px 0", fontSize: "0.95rem", color: "#b91c1c", display: "flex", alignItems: "center", gap: "4px" }}>
            <AlertTriangle size={16}/> Missing Sections (ATS Impact)
          </h3>
          <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "0.85rem", color: "#7f1d1d" }}>
            {data.missing_skills.map((item, idx) => <li key={idx}>{item}</li>)}
          </ul>
        </div>
      )}

      {/* Gemini Analysis Blocks */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        {data.weak_bullet_points && data.weak_bullet_points.length > 0 && (
          <div className="metric-card" style={{ display: "block", background: "#fffbeb", border: "1px solid #fde68a" }}>
            <h4 style={{ margin: "0 0 8px 0", fontSize: "0.9rem", color: "#92400e" }}>Weak Bullet Points</h4>
            <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.8rem", color: "#b45309" }}>
              {data.weak_bullet_points.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>
        )}
        
        {data.grammar_issues && data.grammar_issues.length > 0 && (
          <div className="metric-card" style={{ display: "block", background: "#fef2f2", border: "1px solid #fecaca" }}>
            <h4 style={{ margin: "0 0 8px 0", fontSize: "0.9rem", color: "#991b1b" }}>Grammar & Phrasing</h4>
            <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.8rem", color: "#7f1d1d" }}>
              {data.grammar_issues.map((g, i) => <li key={i}>{g}</li>)}
            </ul>
          </div>
        )}
      </div>

      {data.suggested_improvements && data.suggested_improvements.length > 0 && (
        <div className="metric-card" style={{ display: "block", background: "#f0fdf4", border: "1px solid #bbf7d0" }}>
          <h3 style={{ margin: "0 0 8px 0", fontSize: "0.95rem", color: "#15803d", display: "flex", alignItems: "center", gap: "4px" }}>
            <Lightbulb size={16}/> Actionable Improvements
          </h3>
          <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "0.85rem", color: "#166534" }}>
            {data.suggested_improvements.map((sug, idx) => (
              <li key={idx} style={{ marginBottom: "4px" }}>{sug}</li>
            ))}
          </ul>
        </div>
      )}
      
      {data.future_ready_skills && data.future_ready_skills.length > 0 && (
        <div className="metric-card" style={{ display: "block", background: "#f0f9ff", border: "1px solid #bae6fd" }}>
          <h3 style={{ margin: "0 0 8px 0", fontSize: "0.95rem", color: "#0369a1", display: "flex", alignItems: "center", gap: "4px" }}>
            <CheckCircle size={16}/> Future-Ready Skills to Learn
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {data.future_ready_skills.map((s, i) => (
              <span key={i} style={{ background: "#e0f2fe", color: "#0284c7", padding: "2px 8px", borderRadius: "12px", fontSize: "0.75rem" }}>{s}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
