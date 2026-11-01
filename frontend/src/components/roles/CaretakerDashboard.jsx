import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ROUTE_PATHS } from '../../constants/routes.constants.js';

export const CaretakerDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [driverStatus, setDriverStatus] = useState({
    name: 'Srini (Driver)',
    vehicle: 'Toyota Innova Crysta (KA-01-MJ-9999)',
    safetyScore: 88,
    status: 'NORMAL',
    lastLocation: 'Vijayawada Highway (16.5062, 80.6480)',
    activeSession: 'ACTIVE'
  });

  useEffect(() => {
    fetch('/api/v1/emergency/', { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setAlerts(data))
      .catch(() => {});
  }, []);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0b0f19', color: '#f3f4f6', fontFamily: 'system-ui, -apple-system, sans-serif', padding: '1.75rem' }}>
      <div style={{ maxWidth: '1180px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0, fontWeight: 700 }}>
              SmartRoad <span style={{ color: '#06b6d4' }}>Caretaker Live Safety Monitor</span>
            </h1>
            <p style={{ margin: '0.25rem 0 0 0', opacity: 0.75, fontSize: '0.85rem' }}>
              Assigned Driver Tracker • Real-Time Peril Alerts • Emergency Response
            </p>
          </div>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '0.375rem', backgroundColor: 'rgba(16,185,129,0.15)', color: '#10b981' }}>
            ● CARETAKER ROLE ACTIVE
          </span>
        </div>

        {/* Assigned Driver Card */}
        <div style={{ backgroundColor: 'rgba(6,182,212,0.05)', border: '1px solid rgba(6,182,212,0.2)', borderRadius: '1rem', padding: '1.5rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700 }}>👤 Assigned Driver: {driverStatus.name}</h2>
              <p style={{ margin: '0.2rem 0 0 0', opacity: 0.8, fontSize: '0.85rem' }}>Vehicle: <strong>{driverStatus.vehicle}</strong></p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10b981' }}>{driverStatus.safetyScore} <span style={{ fontSize: '0.85rem', opacity: 0.6 }}>/ 100</span></span>
              <p style={{ margin: 0, fontSize: '0.75rem', color: '#10b981', fontWeight: 700 }}>SAFETY SCORE</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', fontSize: '0.85rem' }}>
            <div style={{ padding: '0.75rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '0.5rem' }}>
              <span style={{ opacity: 0.6, display: 'block' }}>Monitoring Status:</span>
              <strong style={{ color: '#10b981' }}>{driverStatus.activeSession}</strong>
            </div>
            <div style={{ padding: '0.75rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '0.5rem' }}>
              <span style={{ opacity: 0.6, display: 'block' }}>Last Known Location:</span>
              <strong>{driverStatus.lastLocation}</strong>
            </div>
          </div>
        </div>

        {/* Emergency Alert Stream */}
        <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '1rem', padding: '1.25rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.05rem', fontWeight: 600 }}>🚨 Emergency Risk Alert History</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {alerts.length === 0 ? (
              <p style={{ opacity: 0.5, fontSize: '0.85rem', margin: 0 }}>No active emergency alerts for assigned driver.</p>
            ) : (
              alerts.map((al) => (
                <div key={al.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', backgroundColor: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '0.5rem', fontSize: '0.85rem' }}>
                  <div>
                    <strong style={{ color: '#ef4444' }}>{al.alert_type} (Risk: {al.risk_score}/100)</strong>
                    <p style={{ margin: '0.15rem 0 0 0', opacity: 0.8, fontSize: '0.75rem' }}>{al.details}</p>
                  </div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '0.375rem', backgroundColor: 'rgba(255,255,255,0.1)', color: '#fff' }}>
                    {al.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default CaretakerDashboard;
