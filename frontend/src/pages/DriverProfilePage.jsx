import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { ROUTE_PATHS } from '../constants/routes.constants.js';

export const DriverProfilePage = () => {
  const { currentUser } = useAuth();
  const [profile, setProfile] = useState({
    name: currentUser?.name || 'Srini',
    email: currentUser?.email || 'driver@smartroad.ai',
    phone: '+91 98765 43210',
    emergency_contact: '+91 91234 56789 (Father)',
    caretaker_name: 'Anitha (Caretaker)',
    blood_group: 'O+',
    license_no: 'DL-042024-9988',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Srini'
  });

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ ...profile });
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    fetch('/api/v1/profiles/me', { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          setProfile((prev) => ({ ...prev, ...data }));
          setFormData((prev) => ({ ...prev, ...data }));
        }
      })
      .catch(() => {});
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaveStatus('Saving...');
    try {
      const res = await fetch('/api/v1/profiles/me', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
        credentials: 'include'
      });
      if (res.ok) {
        setProfile({ ...formData });
        setIsEditing(false);
        setSaveStatus('Profile updated successfully!');
        setTimeout(() => setSaveStatus(null), 3000);
      }
    } catch (err) {
      setSaveStatus('Failed to update profile.');
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0b0f19', color: '#f3f4f6', fontFamily: 'system-ui, -apple-system, sans-serif', padding: '1.75rem' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0, fontWeight: 700 }}>
              SmartRoad <span style={{ color: '#06b6d4' }}>Driver Profile</span>
            </h1>
            <p style={{ margin: '0.25rem 0 0 0', opacity: 0.75, fontSize: '0.85rem' }}>
              Personal Details • Emergency Contacts • Personalized Baseline Parameters
            </p>
          </div>
          
          <Link to={ROUTE_PATHS.DASHBOARD} style={{ padding: '0.45rem 1rem', borderRadius: '0.5rem', border: '1px solid rgba(6,182,212,0.4)', backgroundColor: 'rgba(6,182,212,0.1)', color: '#06b6d4', fontWeight: 600, textDecoration: 'none', fontSize: '0.85rem' }}>
            📊 Back to Dashboard
          </Link>
        </div>

        {saveStatus && (
          <div style={{ padding: '0.75rem 1rem', backgroundColor: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '0.5rem', color: '#10b981', marginBottom: '1.25rem', fontSize: '0.85rem' }}>
            {saveStatus}
          </div>
        )}

        {/* Profile Card */}
        <div style={{ backgroundColor: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '1rem', padding: '1.75rem' }}>
          
          {/* Avatar & Title Row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '1.75rem', borderBottom: '1px dashed rgba(255,255,255,0.1)', paddingBottom: '1.25rem' }}>
            <img 
              src={profile.avatar_url} 
              alt="Driver Avatar" 
              style={{ width: '80px', height: '80px', borderRadius: '50%', border: '2px solid #06b6d4', backgroundColor: 'rgba(6,182,212,0.1)' }} 
            />
            <div>
              <h2 style={{ margin: 0, fontSize: '1.35rem', fontWeight: 700 }}>{profile.name}</h2>
              <p style={{ margin: '0.2rem 0 0 0', opacity: 0.7, fontSize: '0.85rem' }}>Driver License: <strong>{profile.license_no}</strong></p>
              <span style={{ display: 'inline-block', marginTop: '0.4rem', fontSize: '0.75rem', fontWeight: 700, padding: '0.15rem 0.5rem', borderRadius: '0.25rem', backgroundColor: 'rgba(16,185,129,0.15)', color: '#10b981' }}>
                ● PERSONALIZED BASELINE ACTIVE
              </span>
            </div>

            <div style={{ marginLeft: 'auto' }}>
              {!isEditing ? (
                <button 
                  onClick={() => setIsEditing(true)} 
                  style={{ padding: '0.45rem 1.1rem', borderRadius: '0.5rem', border: '1px solid #06b6d4', backgroundColor: 'rgba(6,182,212,0.1)', color: '#06b6d4', fontWeight: 700, cursor: 'pointer' }}
                >
                  ✏️ Edit Profile
                </button>
              ) : (
                <button 
                  onClick={() => setIsEditing(false)} 
                  style={{ padding: '0.45rem 1.1rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.2)', backgroundColor: 'transparent', color: '#9ca3af', fontWeight: 600, cursor: 'pointer' }}
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Form / Details View */}
          {!isEditing ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
              {[
                { label: 'Full Name', val: profile.name },
                { label: 'Email Address', val: profile.email },
                { label: 'Phone Number', val: profile.phone },
                { label: 'Emergency Contact', val: profile.emergency_contact },
                { label: 'Assigned Caretaker', val: profile.caretaker_name },
                { label: 'Blood Group', val: profile.blood_group }
              ].map((item, i) => (
                <div key={i} style={{ padding: '0.85rem', backgroundColor: 'rgba(255,255,255,0.015)', border: '1px solid rgba(255,255,255,0.03)', borderRadius: '0.5rem' }}>
                  <p style={{ margin: 0, fontSize: '0.75rem', opacity: 0.6 }}>{item.label}</p>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.95rem', fontWeight: 600 }}>{item.val}</p>
                </div>
              ))}
            </div>
          ) : (
            <form onSubmit={handleSave} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', opacity: 0.8, marginBottom: '0.3rem' }}>Full Name</label>
                <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(0,0,0,0.5)', color: '#fff' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', opacity: 0.8, marginBottom: '0.3rem' }}>Phone Number</label>
                <input type="text" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(0,0,0,0.5)', color: '#fff' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', opacity: 0.8, marginBottom: '0.3rem' }}>Emergency Contact</label>
                <input type="text" value={formData.emergency_contact} onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(0,0,0,0.5)', color: '#fff' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', opacity: 0.8, marginBottom: '0.3rem' }}>Blood Group</label>
                <input type="text" value={formData.blood_group} onChange={(e) => setFormData({ ...formData, blood_group: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(0,0,0,0.5)', color: '#fff' }} />
              </div>

              <div style={{ gridColumn: '1 / -1', marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                <button type="submit" style={{ padding: '0.55rem 1.5rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#10b981', color: '#000', fontWeight: 700, cursor: 'pointer' }}>
                  💾 Save Profile Changes
                </button>
              </div>
            </form>
          )}

        </div>

      </div>
    </div>
  );
};

export default DriverProfilePage;
