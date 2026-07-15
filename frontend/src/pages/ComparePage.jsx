import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '../store';
import { ArrowLeft, Scale } from 'lucide-react';
import ComparisonTable from './ComparisonTable';
import ExportButton from '../components/ExportButton';
import './ComparePage.css';

export default function ComparePage() {
  const navigate = useNavigate();
  const selectedComparison = useChatStore((state) => state.selectedComparison);

  return (
    <div className="compare-page-container">
      <div className="compare-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button className="back-button" onClick={() => navigate(-1)}>
            <ArrowLeft size={18} /> Back to Chat
          </button>
          <h1 className="compare-title" style={{ margin: 0 }}>
            <Scale size={24} className="compare-icon" /> College Comparison
          </h1>
        </div>
        {selectedComparison && selectedComparison.length > 0 && (
          <ExportButton exportType="college_comparison" title="College Comparison Report" data={{ colleges: selectedComparison }} />
        )}
      </div>

      <div className="compare-content">
        {!selectedComparison || selectedComparison.length === 0 ? (
          <div className="compare-empty-state">
            <div className="empty-illustration">
              <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="empty-svg">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="var(--border-color)"/>
                <line x1="9" y1="3" x2="9" y2="21" stroke="var(--border-color)"/>
                <line x1="15" y1="3" x2="15" y2="21" stroke="var(--border-color)"/>
                <line x1="3" y1="9" x2="21" y2="9" stroke="var(--border-color)"/>
                <line x1="3" y1="15" x2="21" y2="15" stroke="var(--border-color)"/>
              </svg>
            </div>
            <h2>No colleges selected</h2>
            <p>Go back to the chat and select up to 3 colleges to compare them side-by-side.</p>
            <button className="btn-primary" onClick={() => navigate(-1)}>
              <ArrowLeft size={16} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} /> Return to Chat
            </button>
          </div>
        ) : (
          <ComparisonTable colleges={selectedComparison} />
        )}
      </div>
    </div>
  );
}
