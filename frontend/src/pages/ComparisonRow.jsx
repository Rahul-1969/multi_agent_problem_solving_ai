import React from 'react';

// Helper to get nested value by string path e.g. "a.b.c"
const getNestedValue = (obj, path) => {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj);
};

export default function ComparisonRow({ field, colleges }) {
  // Extract values for this field across all colleges
  const values = colleges.map(c => getNestedValue(c, field.path));
  
  // Array to hold the assigned rank class for each column (e.g. "rank-1", "rank-2", "rank-3")
  const ranks = new Array(values.length).fill('');
  
  if (field.best !== 'none' && colleges.length > 1) {
    // Filter out N/A or invalid numbers for comparison
    const numValues = values.map((v, i) => {
      const num = parseFloat(v);
      return { val: isNaN(num) ? null : num, index: i };
    }).filter(item => item.val !== null);

    if (numValues.length > 0) {
      // Sort values based on the "best" criteria
      // If 'max' is best, sort descending. If 'min' is best, sort ascending.
      const sorted = [...numValues].sort((a, b) => {
        return field.best === 'max' ? b.val - a.val : a.val - b.val;
      });
      
      // Assign ranks (handling ties)
      let currentRank = 1;
      let prevVal = sorted[0].val;
      
      sorted.forEach((item, idx) => {
        if (item.val !== prevVal) {
          currentRank = idx + 1; // e.g. if 1st and 2nd are tied, next is 3rd
          prevVal = item.val;
        }
        // Only assign colors for top 3
        if (currentRank <= 3) {
          ranks[item.index] = `rank-${currentRank}`;
        }
      });
    }
  }

  return (
    <tr>
      <td className="compare-label">{field.label}</td>
      {values.map((v, i) => (
        <td key={i} className={`compare-value ${ranks[i]}`}>
          {field.format(v)}
        </td>
      ))}
    </tr>
  );
}
