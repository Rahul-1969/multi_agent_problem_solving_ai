import React, { useEffect, useState } from 'react';
import CareerPlanCard from '../components/CareerPlanCard';
import ExportButton from '../components/ExportButton';
import apiService from '../services/apiService';

export default function CareerPlansPage() {
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const res = await apiService.get('/api/v1/profile/career-plans');
      setPlans(res.data.plans || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRename = async (id, newName) => {
    try {
      await apiService.put(`/api/v1/profile/career-plans/${id}`, { career_goal: newName });
      fetchPlans();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure?")) return;
    try {
      await apiService.delete(`/api/v1/profile/career-plans/${id}`);
      fetchPlans();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDuplicate = async (id) => {
    try {
      await apiService.post(`/api/v1/profile/career-plans/${id}/duplicate`);
      fetchPlans();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>Saved Career Plans</h1>
      </div>
      
      <div>
        {plans.map(p => (
          <div key={p.id} style={{ position: 'relative' }}>
            <CareerPlanCard 
              plan={p} 
              onView={(plan) => console.log('View', plan)}
              onRename={handleRename}
              onDelete={handleDelete}
              onDuplicate={handleDuplicate}
            />
            <div style={{ position: 'absolute', top: '16px', right: '16px' }}>
              <ExportButton exportType="career_roadmap" title={p.career_goal} data={p.roadmap} label="Export Plan" />
            </div>
          </div>
        ))}
        {plans.length === 0 && <p>No saved career plans yet.</p>}
      </div>
    </div>
  );
}
