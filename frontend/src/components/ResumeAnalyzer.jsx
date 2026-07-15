import React from 'react';
import { FileText } from 'lucide-react';
import ResumeScore from './ResumeScore';
import './CollegeResponse.css'; // Reuse CSS

export default function ResumeAnalyzer({ data }) {
  if (!data) return null;

  return (
    <div className="college-response-container">
      <div className="college-response-header" style={{ background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)" }}>
        <FileText className="college-header-icon" size={28} />
        <div>
          <h2 className="college-name">Resume Analysis</h2>
          <p className="college-type">ATS Score: {data.ats_score ?? "N/A"}/100</p>
        </div>
      </div>
      
      <div className="college-response-body">
        <ResumeScore data={data} />
      </div>
    </div>
  );
}
