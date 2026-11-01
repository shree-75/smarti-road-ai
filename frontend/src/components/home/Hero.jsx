import React from 'react';
import { Camera, Activity, MapPin, Eye, Shield, ArrowRight, Play } from 'lucide-react';
import './Hero.css';
const TECH_BADGES = [
  'OpenCV',
  'AI Vision',
  'ESP32',
  'GPS',
  'Emergency Alerts'
];
const DASHBOARD_CARDS = [
  {
    id: 'driver-status',
    icon: Camera,
    label: 'Driver Status',
    value: 'Monitoring',
    footerLabel: 'State',
    footerValue: 'Active',
    theme: 'cyan'
  },
  {
    id: 'heart-rate',
    icon: Activity,
    label: 'Heart Rate',
    value: 'Connected',
    type: 'biometrics',
    theme: 'violet'
  },
  {
    id: 'ai-vision',
    icon: Eye,
    label: 'AI Vision',
    value: 'Processing',
    type: 'camera',
    theme: 'emerald',
    className: 'camera-card'
  },
  {
    id: 'gps-tracking',
    icon: MapPin,
    label: 'GPS Tracking',
    value: 'Live',
    type: 'gps',
    theme: 'cyan'
  },
  {
    id: 'safety-score',
    icon: Shield,
    label: 'Safety Score',
    value: 'Ready',
    type: 'score',
    theme: 'cyan',
    className: 'score-card'
  }
];
const Hero = () => {
  const renderCardGraphic = (card) => {
    switch (card.type) {
      case 'biometrics':
        return (
          <div className="card-graph">
            <svg viewBox="0 0 120 30" className="heart-wave" aria-hidden="true">
              <path
                d="M0 15 H35 L40 5 L45 25 L50 12 L55 18 L60 15 H120"
                fill="none"
                stroke="var(--color-violet, #8b5cf6)"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        );
      case 'camera':
        return (
          <div className="camera-preview">
            <div className="scanline"></div>
            <div className="camera-grid-overlay"></div>
            <div className="camera-target-reticle"></div>
            <span className="fps-counter">Active</span>
            <span className="rec-indicator">
              <span className="red-dot"></span>Live
            </span>
          </div>
        );
      case 'gps':
        return (
          <div className="gps-details">
            <div className="gps-row">
              <span className="gps-coord-label">Signal</span>
              <span className="gps-coord-val">Connected</span>
            </div>
            <div className="gps-row">
              <span className="gps-coord-label">Status</span>
              <span className="gps-coord-val">Active</span>
            </div>
          </div>
        );
      case 'score':
        return (
          <div className="score-circle-wrapper">
            <svg width="56" height="56" viewBox="0 0 36 36" className="circular-progress" aria-hidden="true">
              <path
                className="circle-bg"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="rgba(255, 255, 255, 0.05)"
                strokeWidth="3.5"
              />
              <path
                className="circle"
                strokeDasharray="85, 100"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="var(--color-cyan, #06b6d4)"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
            </svg>
          </div>
        );
      default:
        return null;
    }
  };
  return (
    <section className="hero" id="home">
      <div className="hero-background">
        <div className="glow-orb orb-blue"></div>
        <div className="glow-orb orb-violet"></div>
      </div>
      
      <div className="hero-container">
        {/* Left Column */}
        <div className="hero-content">
          <div className="hero-badge-wrapper">
            <span className="hero-tag-badge">AI Safety Core</span>
          </div>
          
          <h1 className="hero-title">
            SmartRoad <span className="text-gradient">AI</span>
          </h1>
          
          <h2 className="hero-subtitle">
            AI-Powered Intelligent Road Safety & Driver Monitoring Platform
          </h2>
          
          <p className="hero-description">
            Prevent accidents before they happen using Artificial Intelligence, Computer Vision, IoT Sensors, and Real-Time Analytics.
          </p>
          
          <div className="hero-ctas">
            <a href="#features" className="btn-primary">
              Start Monitoring <ArrowRight size={18} className="cta-icon" />
            </a>
            <button className="btn-secondary">
              <Play size={18} className="cta-icon" fill="currentColor" /> View Demo
            </button>
          </div>
          
          <div className="hero-features-badges">
            <p className="badges-label">Integrated Technologies:</p>
            <div className="badges-list">
              {TECH_BADGES.map((badge) => (
                <span key={badge} className="feature-badge">
                  <span className="checkmark">✓</span> {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        {/* Right Column (Mapped dashboard cards) */}
        <div className="hero-visual">
          <div className="dashboard-mockup">
            <div className="dashboard-header">
              <div className="dashboard-status">
                <span className="status-dot pulsing"></span>
                <span className="status-text">MONITORING</span>
              </div>
              <div className="dashboard-title">Interface Hub</div>
            </div>
            
            <div className="dashboard-grid">
              {DASHBOARD_CARDS.map((card) => (
                <div key={card.id} className={`dashboard-card ${card.className || ''}`}>
                  <div className="card-top">
                    <div className={`card-icon-wrapper ${card.theme}`}>
                      <card.icon size={20} aria-hidden="true" />
                    </div>
                    <div className="card-meta">
                      <span className="card-label">{card.label}</span>
                      <span className={`card-value text-${card.theme}`}>{card.value}</span>
                    </div>
                  </div>
                  {renderCardGraphic(card)}
                  {card.footerLabel && (
                    <div className="card-footer">
                      <span className="footer-label">{card.footerLabel}</span>
                      <span className="footer-value">{card.footerValue}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
export default Hero;