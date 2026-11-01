import React from 'react';

export const AdminDashboard = () => {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0b0f19', color: '#f3f4f6', fontFamily: 'system-ui, -apple-system, sans-serif', padding: '1.75rem' }}>
      <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0, fontWeight: 700 }}>
              SmartRoad <span style={{ color: '#06b6d4' }}>System Administrator Command Center</span>
            </h1>
            <p style={{ margin: '0.25rem 0 0 0', opacity: 0.75, fontSize: '0.85rem' }}>
              System Health • Active WebSocket Streams • Database Metrics
            </p>
          </div>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '0.375rem', backgroundColor: 'rgba(6,182,212,0.15)', color: '#06b6d4' }}>
            🛡️ ADMIN ROLE ACTIVE
          </span>
        </div>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
          {[
            { title: 'Registered Users', val: '14 Active', icon: '👥' },
            { title: 'Active Driver Sessions', val: '1 Monitoring', icon: '🚗' },
            { title: 'WebSocket Pipeline', val: '● LIVE (15 FPS)', icon: '⚡' },
            { title: 'Emergency Alerts', val: '0 Active', icon: '🚨' }
          ].map((st, i) => (
            <div key={i} style={{ padding: '1.25rem', backgroundColor: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0.75rem' }}>
              <span style={{ fontSize: '1.75rem' }}>{st.icon}</span>
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.75rem', opacity: 0.6 }}>{st.title}</p>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '1.15rem', fontWeight: 700, color: '#06b6d4' }}>{st.val}</p>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default AdminDashboard;
