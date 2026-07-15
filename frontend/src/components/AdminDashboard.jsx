import React, { useState, useEffect } from 'react';
import { Activity, Users, FileText, Database } from 'lucide-react';

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [activeTab, setActiveTab] = useState('metrics');

  useEffect(() => {
    fetchMetrics();
    fetchUsers();
    fetchLogs();
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/v1/admin/metrics');
      const data = await res.json();
      if (data.status === 'success') setMetrics(data.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch('/api/v1/admin/users');
      const data = await res.json();
      if (data.status === 'success') setUsers(data.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch('/api/v1/admin/logs');
      const data = await res.json();
      if (data.status === 'success') setLogs(data.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Activity size={28} color="#4f46e5"/> System Dashboard
      </h1>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #e5e7eb' }}>
        <button 
          onClick={() => setActiveTab('metrics')}
          style={{ padding: '8px 16px', background: activeTab === 'metrics' ? '#4f46e5' : 'transparent', color: activeTab === 'metrics' ? 'white' : '#4b5563', border: 'none', borderRadius: '4px 4px 0 0', cursor: 'pointer', fontWeight: 'bold' }}>
          Overview
        </button>
        <button 
          onClick={() => setActiveTab('users')}
          style={{ padding: '8px 16px', background: activeTab === 'users' ? '#4f46e5' : 'transparent', color: activeTab === 'users' ? 'white' : '#4b5563', border: 'none', borderRadius: '4px 4px 0 0', cursor: 'pointer', fontWeight: 'bold' }}>
          Users
        </button>
        <button 
          onClick={() => setActiveTab('logs')}
          style={{ padding: '8px 16px', background: activeTab === 'logs' ? '#4f46e5' : 'transparent', color: activeTab === 'logs' ? 'white' : '#4b5563', border: 'none', borderRadius: '4px 4px 0 0', cursor: 'pointer', fontWeight: 'bold' }}>
          System Logs
        </button>
      </div>

      {activeTab === 'metrics' && metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.875rem', textTransform: 'uppercase' }}>CPU Usage</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827' }}>{metrics.cpu_usage_pct}%</div>
          </div>
          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.875rem', textTransform: 'uppercase' }}>Memory Usage</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827' }}>{metrics.memory_usage_pct}%</div>
          </div>
          <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#6b7280', fontSize: '0.875rem', textTransform: 'uppercase' }}>Active Users</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827' }}>{metrics.active_users}</div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: '#f9fafb' }}>
              <tr>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '0.875rem', color: '#6b7280', fontWeight: '600' }}>Username</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '0.875rem', color: '#6b7280', fontWeight: '600' }}>Created At</th>
                <th style={{ padding: '12px 24px', textAlign: 'left', fontSize: '0.875rem', color: '#6b7280', fontWeight: '600' }}>Last Login</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u, i) => (
                <tr key={i} style={{ borderTop: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '12px 24px', color: '#111827' }}>{u.username}</td>
                  <td style={{ padding: '12px 24px', color: '#6b7280' }}>{u.created_at}</td>
                  <td style={{ padding: '12px 24px', color: '#6b7280' }}>{u.last_login}</td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr><td colSpan="3" style={{ padding: '24px', textAlign: 'center', color: '#6b7280' }}>No users found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'logs' && (
        <div style={{ background: '#1f2937', color: '#f3f4f6', padding: '1.5rem', borderRadius: '8px', height: '500px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.875rem' }}>
          {logs.map((log, i) => (
            <div key={i} style={{ marginBottom: '4px', whiteSpace: 'pre-wrap' }}>{log}</div>
          ))}
          {logs.length === 0 && <div style={{ color: '#9ca3af' }}>No logs available.</div>}
        </div>
      )}
    </div>
  );
}
