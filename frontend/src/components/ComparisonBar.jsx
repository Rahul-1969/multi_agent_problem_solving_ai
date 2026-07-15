import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../store';
import { X, Scale } from 'lucide-react';
import './ComparisonBar.css';

export default function ComparisonBar() {
  const navigate = useNavigate();
  const selectedComparison = useChatStore((state) => state.selectedComparison);
  const clearComparison = useChatStore((state) => state.clearComparison);

  if (!selectedComparison || selectedComparison.length === 0) {
    return null;
  }

  const handleCompare = () => {
    navigate('/compare');
  };

  return (
    <div className="comparison-bar">
      <div className="comparison-info">
        <span className="comparison-count">{selectedComparison.length} / 3 Selected</span>
        <div className="comparison-chips">
          {selectedComparison.map((c) => (
            <span key={c.college_code} className="comparison-chip">
              {c.college_code}
            </span>
          ))}
        </div>
      </div>
      <div className="comparison-actions">
        <button className="btn-clear" onClick={clearComparison}>
          <X size={14} /> Clear
        </button>
        <button 
          className="btn-compare" 
          disabled={selectedComparison.length < 2}
          onClick={handleCompare}
        >
          <Scale size={14} /> Compare
        </button>
      </div>
    </div>
  );
}
