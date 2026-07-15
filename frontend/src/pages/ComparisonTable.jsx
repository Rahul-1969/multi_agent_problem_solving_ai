import React from 'react';
import { comparisonFields } from './comparisonFields';
import ComparisonRow from './ComparisonRow';
import { useChatStore } from '../store';
import { X } from 'lucide-react';

export default function ComparisonTable({ colleges }) {
  const removeComparison = useChatStore((state) => state.removeComparison);

  if (!colleges || colleges.length === 0) return null;

  return (
    <div className="compare-table-wrapper">
      <table className="compare-table">
        <thead>
          <tr>
            <th className="compare-header-label">Metric</th>
            {colleges.map((c, i) => (
              <th key={i} className="compare-header-college">
                <div className="college-header-top">
                  <div className="college-code">{c.college_code}</div>
                  <button 
                    className="btn-remove-college" 
                    onClick={() => removeComparison(c.college_code)}
                    title="Remove from comparison"
                  >
                    <X size={14} /> Remove
                  </button>
                </div>
                <div className="college-name">{c.college_name}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="compare-label">Predicted Branches</td>
            {colleges.map((c, i) => (
              <td key={i} className="compare-value branch-value">
                {c.predicted_branches ? c.predicted_branches.join(", ") : "N/A"}
              </td>
            ))}
          </tr>
          <tr>
            <td className="compare-label">Admission Chance</td>
            {colleges.map((c, i) => (
              <td key={i} className={`compare-value admission-chance ${c.admission_probability?.toLowerCase()}`}>
                {c.admission_probability || "N/A"}
              </td>
            ))}
          </tr>
          {comparisonFields.map((field, idx) => (
            <ComparisonRow key={idx} field={field} colleges={colleges} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
