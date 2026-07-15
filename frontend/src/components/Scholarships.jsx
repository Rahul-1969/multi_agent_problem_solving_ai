import React from 'react';
import { Award, Calendar, DollarSign, ExternalLink } from 'lucide-react';
import MarkdownRenderer from './MarkdownRenderer';
import './CollegeResponse.css'; // Reuse styles where possible

import ScholarshipCard from './ScholarshipCard';

export default function Scholarships({ data }) {
  if (!data || !data.scholarships || data.scholarships.length === 0) {
    return <div className="bot-message-content">No scholarships found.</div>;
  }

  return (
    <div className="college-response-container">
      <div className="college-response-header" style={{ background: "linear-gradient(135deg, #10b981 0%, #059669 100%)" }}>
        <Award className="college-header-icon" size={28} />
        <div>
          <h2 className="college-name">Scholarship Matches</h2>
          <p className="college-type">Based on your profile</p>
        </div>
      </div>
      
      <div className="college-response-body">
        {data.scholarships.map((scholarship, idx) => (
          <ScholarshipCard key={idx} scholarship={scholarship} />
        ))}
      </div>
    </div>
  );
}
