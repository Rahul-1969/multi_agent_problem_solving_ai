import React from 'react';

export default function CareerPlanCard({ plan, onView, onRename, onDelete, onDuplicate }) {
  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '20px',
      backgroundColor: '#ffffff',
      marginBottom: '16px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 style={{ margin: '0 0 8px 0', color: '#111827', fontSize: '20px' }}>
            {plan.career_goal}
          </h3>
          <p style={{ margin: '0 0 16px 0', color: '#6b7280', fontSize: '14px' }}>
            Created: {new Date(plan.created_at).toLocaleDateString()}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            onClick={() => onView(plan)}
            style={{ padding: '6px 12px', backgroundColor: '#4f46e5', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            View Roadmap
          </button>
          <button 
            onClick={() => {
              const newName = prompt("Enter new goal name:", plan.career_goal);
              if (newName) onRename(plan.id, newName);
            }}
            style={{ padding: '6px 12px', backgroundColor: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db', borderRadius: '4px', cursor: 'pointer' }}
          >
            Rename
          </button>
          <button 
            onClick={() => onDuplicate(plan.id)}
            style={{ padding: '6px 12px', backgroundColor: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db', borderRadius: '4px', cursor: 'pointer' }}
          >
            Duplicate
          </button>
          <button 
            onClick={() => onDelete(plan.id)}
            style={{ padding: '6px 12px', backgroundColor: '#fee2e2', color: '#dc2626', border: '1px solid #fca5a5', borderRadius: '4px', cursor: 'pointer' }}
          >
            Delete
          </button>
        </div>
      </div>
      
      <div style={{ marginTop: '12px' }}>
        <p style={{ margin: 0, color: '#4b5563' }}>
          <strong>{plan.roadmap?.roadmap_steps?.length || 0}</strong> Milestone Steps
        </p>
      </div>
    </div>
  );
}
