import React, { useState, useEffect } from 'react';

export const PoliceDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/emergency/', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (err) {
      console.error('Failed to fetch police alerts:', err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleUpdateStatus = async (id, newStatus) => {
    try {
      const res = await fetch(`/api/v1/emergency/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
        credentials: 'include'
      });
      if (res.ok) {
        fetchAlerts();
      }
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0b0f19', color: '#f3f4f6', fontFamily: 'system-ui, -apple-system, sans-serif', padding: '1.75rem' }}>
      <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0, fontWeight: 700 }}>
              SmartRoad <span style={{ color: '#3b82f6' }}>Highway Police Traffic Command</span>
            </h1>
            <p style={{ margin: '0.25rem 0 0 0', opacity: 0.75, fontSize: '0.85rem' }}>
              Real-Time Highway Incident Monitor • Vehicle Plate Lookup • Dispatch Status
            </p>
          </div>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '0.375rem', backgroundColor: 'rgba(59,130,246,0.15)', color: '#3b82f6' }}>
            🚓 POLICE ROLE ACTIVE
          </span>
        </div>

        {/* Police Incident Stream */}
        <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '1rem', padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.05rem', fontWeight: 600 }}>🚔 Live Highway Incident Log</h3>

          {loading ? (
            <p style={{ opacity: 0.7 }}>Loading incident stream...</p>
          ) : alerts.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', opacity: 0.5 }}>No active highway incidents logged.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {alerts.map((al) => (
                <div key={al.id} style={{ padding: '1rem', backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '1rem', color: '#3b82f6' }}>{al.alert_type}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', padding: '0.15rem 0.5rem', borderRadius: '0.25rem' }}>
                        RISK: {al.risk_score}/100
                      </span>
                    </div>
                    <p style={{ margin: '0.3rem 0 0 0', fontSize: '0.85rem', opacity: 0.8 }}>{al.details}</p>
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <button onClick={() => handleUpdateStatus(al.id, 'ACKNOWLEDGED')} style={{ padding: '0.35rem 0.75rem', borderRadius: '0.4rem', border: '1px solid #3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', color: '#3b82f6', fontWeight: 700, cursor: 'pointer', fontSize: '0.75rem' }}>
                      Acknowledge
                    </button>
                    <button onClick={() => handleUpdateStatus(al.id, 'RESOLVED')} style={{ padding: '0.35rem 0.75rem', borderRadius: '0.4rem', border: 'none', backgroundColor: '#10b981', color: '#000', fontWeight: 700, cursor: 'pointer', fontSize: '0.75rem' }}>
                      Resolve
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default PoliceDashboard;
