import React from 'react';
import { Route } from 'lucide-react';
import CareerTimeline from './CareerTimeline';
import './CollegeResponse.css'; // Reuse some CSS

export default function CareerRoadmap({ data }) {
  if (!data || (!data.roadmap_steps && !data.timeline)) {
    return <div className="bot-message-content">No roadmap available.</div>;
  }

  return (
    <div className="college-response-container">
      <div className="college-response-header" style={{ background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)" }}>
        <Route className="college-header-icon" size={28} />
        <div>
          <h2 className="college-name">Career Roadmap</h2>
          <p className="college-type">{data.timeline || "Step-by-step guide"}</p>
        </div>
      </div>
      
      <div className="college-response-body">
        {data.salary_progression && (
          <div style={{ marginBottom: "1rem", padding: "10px", background: "#f0fdf4", color: "#166534", borderRadius: "6px" }}>
            <strong>Salary Progression:</strong> {data.salary_progression}
          </div>
        )}
        
        <CareerTimeline roadmap={data} />
        
        {data.certifications && data.certifications.length > 0 && (
          <div style={{ marginTop: "1.5rem" }}>
            <h4 style={{ margin: "0 0 8px 0" }}>Recommended Certifications</h4>
            <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.9rem", color: "#4b5563" }}>
              {data.certifications.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
