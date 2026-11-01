import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { CarLogo } from '../components/common/CarLogo.jsx';
import { ROUTE_PATHS } from '../constants/routes.constants.js';

export const VehicleManagement = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  
  const [newVehicle, setNewVehicle] = useState({
    manufacturer: 'Toyota',
    model_name: 'Innova Crysta',
    variant: '2.8Z AT',
    year: 2024,
    license_plate: 'KA-01-MJ-9999',
    color: 'Pearl White',
    fuel_type: 'Diesel'
  });

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/vehicles/', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setVehicles(data);
      }
    } catch (err) {
      console.error('Failed to load vehicles:', err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchVehicles();
  }, []);

  const handleAddVehicle = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/vehicles/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newVehicle),
        credentials: 'include'
      });
      if (res.ok) {
        setShowAddModal(false);
        fetchVehicles();
      }
    } catch (err) {
      console.error('Failed to add vehicle:', err);
    }
  };

  const handleDeleteVehicle = async (id) => {
    if (!window.confirm('Delete this vehicle profile?')) return;
    try {
      const res = await fetch(`/api/v1/vehicles/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (res.ok) {
        fetchVehicles();
      }
    } catch (err) {
      console.error('Failed to delete vehicle:', err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0b0f19', color: '#f3f4f6', fontFamily: 'system-ui, -apple-system, sans-serif', padding: '1.75rem' }}>
      <div style={{ maxWidth: '1080px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', margin: 0, fontWeight: 700 }}>
              SmartRoad <span style={{ color: '#06b6d4' }}>Vehicle Management</span>
            </h1>
            <p style={{ margin: '0.25rem 0 0 0', opacity: 0.75, fontSize: '0.85rem' }}>
              Car Brand Logos • License Plate Specifications • Telemetry Association
            </p>
          </div>
          
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button onClick={() => setShowAddModal(true)} style={{ padding: '0.45rem 1.1rem', borderRadius: '0.5rem', border: 'none', backgroundColor: '#10b981', color: '#000', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}>
              ➕ Add New Vehicle
            </button>
            <Link to={ROUTE_PATHS.DASHBOARD} style={{ padding: '0.45rem 1rem', borderRadius: '0.5rem', border: '1px solid rgba(6,182,212,0.4)', backgroundColor: 'rgba(6,182,212,0.1)', color: '#06b6d4', fontWeight: 600, textDecoration: 'none', fontSize: '0.85rem' }}>
              📊 Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Vehicles Grid */}
        {loading ? (
          <p style={{ opacity: 0.7 }}>Loading vehicle profiles...</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
            {vehicles.map((v) => (
              <div key={v.id} style={{ backgroundColor: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '1rem', padding: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                  <CarLogo manufacturer={v.manufacturer} size={48} />
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700 }}>{v.manufacturer} {v.model_name}</h3>
                    <p style={{ margin: '0.15rem 0 0 0', opacity: 0.7, fontSize: '0.8rem' }}>{v.variant || 'Standard'} ({v.year})</p>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem', fontSize: '0.8rem' }}>
                  <div style={{ padding: '0.5rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '0.5rem' }}>
                    <span style={{ opacity: 0.6, display: 'block' }}>Registration No:</span>
                    <strong style={{ color: '#06b6d4' }}>{v.license_plate}</strong>
                  </div>
                  <div style={{ padding: '0.5rem', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '0.5rem' }}>
                    <span style={{ opacity: 0.6, display: 'block' }}>Fuel & Color:</span>
                    <strong>{v.fuel_type} • {v.color}</strong>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                  <button onClick={() => handleDeleteVehicle(v.id)} style={{ padding: '0.3rem 0.75rem', borderRadius: '0.375rem', border: '1px solid rgba(239,68,68,0.3)', backgroundColor: 'transparent', color: '#ef4444', fontSize: '0.75rem', cursor: 'pointer' }}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Add Vehicle Modal */}
        {showAddModal && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '1rem', padding: '1.75rem', width: '450px' }}>
              <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.2rem' }}>Add New Vehicle</h3>
              
              <form onSubmit={handleAddVehicle} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', opacity: 0.8 }}>Manufacturer</label>
                  <select value={newVehicle.manufacturer} onChange={(e) => setNewVehicle({ ...newVehicle, manufacturer: e.target.value })} style={{ width: '100%', padding: '0.45rem', borderRadius: '0.4rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: '#000', color: '#fff' }}>
                    <option value="Toyota">Toyota</option>
                    <option value="Hyundai">Hyundai</option>
                    <option value="Tesla">Tesla</option>
                    <option value="BMW">BMW</option>
                    <option value="Mercedes-Benz">Mercedes-Benz</option>
                    <option value="Ford">Ford</option>
                    <option value="Honda">Honda</option>
                    <option value="Tata">Tata</option>
                    <option value="Mahindra">Mahindra</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', opacity: 0.8 }}>Model Name</label>
                  <input type="text" value={newVehicle.model_name} onChange={(e) => setNewVehicle({ ...newVehicle, model_name: e.target.value })} style={{ width: '100%', padding: '0.45rem', borderRadius: '0.4rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: '#000', color: '#fff' }} required />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', opacity: 0.8 }}>License Plate</label>
                  <input type="text" value={newVehicle.license_plate} onChange={(e) => setNewVehicle({ ...newVehicle, license_plate: e.target.value })} style={{ width: '100%', padding: '0.45rem', borderRadius: '0.4rem', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: '#000', color: '#fff' }} required />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1rem' }}>
                  <button type="button" onClick={() => setShowAddModal(false)} style={{ padding: '0.45rem 1rem', borderRadius: '0.4rem', border: '1px solid rgba(255,255,255,0.2)', backgroundColor: 'transparent', color: '#9ca3af', cursor: 'pointer' }}>Cancel</button>
                  <button type="submit" style={{ padding: '0.45rem 1rem', borderRadius: '0.4rem', border: 'none', backgroundColor: '#10b981', color: '#000', fontWeight: 700, cursor: 'pointer' }}>Save Vehicle</button>
                </div>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default VehicleManagement;
