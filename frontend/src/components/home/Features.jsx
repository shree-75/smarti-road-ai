import React from 'react';
import { Camera, Eye, Wind, Activity, MapPin, ShieldAlert, BarChart3, BellRing } from 'lucide-react';
import './Features.css';
// Centralised configuration array for feature items declared at module level
const FEATURES = [
  {
    id: 'driver-monitoring',
    title: 'Driver Monitoring',
    description: 'Continuous camera-based tracking monitoring facial vectors, alignment, and gaze status.',
    icon: Camera,
    theme: 'cyan',
    previewType: 'camera',
    featureKey: 'camera',
    initialStatus: 'Active'
  },
  {
    id: 'drowsiness-detection',
    title: 'Drowsiness Detection',
    description: 'Fatigue analysis calculating Eye Aspect Ratio (EAR) alerts for micro-sleep events.',
    icon: Eye,
    theme: 'violet',
    previewType: 'drowsiness',
    featureKey: 'drowsiness',
    initialStatus: 'Monitoring'
  },
  {
    id: 'alcohol-detection',
    title: 'Alcohol Detection',
    description: 'Integrates with IoT gas sensors to measure air quality thresholds prior to engine start.',
    icon: Wind,
    theme: 'cyan',
    previewType: 'alcohol',
    featureKey: 'alcohol',
    initialStatus: 'Connected'
  },
  {
    id: 'heart-rate-monitoring',
    title: 'Heart Rate Monitoring',
    description: 'Companion wearable integration checking driver stress profiles and biometrics.',
    icon: Activity,
    theme: 'violet',
    previewType: 'heart-rate',
    featureKey: 'heart-rate',
    initialStatus: 'Connected'
  },
  {
    id: 'gps-tracking',
    title: 'GPS Tracking',
    description: 'Satellite positioning delivering route tracking coordinates and velocity checkpoints.',
    icon: MapPin,
    theme: 'cyan',
    previewType: 'gps',
    featureKey: 'gps',
    initialStatus: 'Live'
  },
  {
    id: 'accident-detection',
    title: 'Accident Detection',
    description: 'G-force shock telematics monitoring vehicle coordinates to instantly register impacts.',
    icon: ShieldAlert,
    theme: 'violet',
    previewType: 'accident',
    featureKey: 'accident',
    initialStatus: 'Monitoring'
  },
  {
    id: 'ai-analytics',
    title: 'AI Analytics',
    description: 'Aggregated safety scores compiled from driving behaviors, braking profiles, and speed rules.',
    icon: BarChart3,
    theme: 'emerald',
    previewType: 'analytics',
    featureKey: 'analytics',
    initialStatus: 'Ready'
  },
  {
    id: 'emergency-sos',
    title: 'Emergency SOS',
    description: 'Automatic safety alert networks broadcasting coordinates and alert codes to response units.',
    icon: BellRing,
    theme: 'emerald',
    previewType: 'sos',
    featureKey: 'sos',
    initialStatus: 'Ready'
  }
];
// Stateless helper function to render HTML/CSS dashboard previews
const renderPreview = (type) => {
  switch (type) {
    case 'camera':
      return (
        <div className="preview-content camera-preview">
          <div className="preview-viewfinder" aria-hidden="true"></div>
          <div className="preview-scanline" aria-hidden="true"></div>
          <div className="preview-face-reticle" aria-hidden="true"></div>
        </div>
      );
    case 'drowsiness':
      return (
        <div className="preview-content drowsiness-preview">
          <div className="preview-eye-graphic" aria-hidden="true">
            <div className="eye-contour"></div>
            <div className="eye-pupil"></div>
          </div>
          <div className="preview-warning-beacon pulsing" aria-hidden="true"></div>
        </div>
      );
    case 'alcohol':
      return (
        <div className="preview-content alcohol-preview" aria-hidden="true">
          <div className="sensor-meter-track">
            <div className="sensor-meter-fill"></div>
          </div>
        </div>
      );
    case 'heart-rate':
      return (
        <div className="preview-content heart-rate-preview">
          <svg viewBox="0 0 120 30" className="preview-ecg-chart" aria-hidden="true">
            <path
              d="M0 15 H35 L40 5 L45 25 L50 12 L55 18 L60 15 H120"
              fill="none"
              stroke="var(--color-violet, #8b5cf6)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      );
    case 'gps':
      return (
        <div className="preview-content gps-preview">
          <div className="preview-map-grid" aria-hidden="true"></div>
          <svg viewBox="0 0 100 40" className="preview-route-path" aria-hidden="true">
            <path
              d="M 10,25 Q 40,5 60,30 T 90,10"
              fill="none"
              stroke="var(--color-cyan, #06b6d4)"
              strokeWidth="2"
              strokeDasharray="4 3"
              strokeLinecap="round"
            />
            <circle cx="90" cy="10" r="3.5" fill="var(--color-cyan, #06b6d4)" className="map-indicator-dot" />
          </svg>
        </div>
      );
    case 'accident':
      return (
        <div className="preview-content accident-preview">
          <svg viewBox="0 0 100 40" className="preview-telemetry-chart" aria-hidden="true">
            <path
              d="M 5,35 L 35,35 L 45,35 L 50,5 L 55,35 L 95,35"
              fill="none"
              stroke="var(--color-violet, #8b5cf6)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      );
    case 'analytics':
      return (
        <div className="preview-content analytics-preview" aria-hidden="true">
          <div className="preview-bar-row">
            <div className="preview-bar-track">
              <div className="preview-bar-fill cyan-fill" style={{ width: '80%' }}></div>
            </div>
          </div>
          <div className="preview-bar-row">
            <div className="preview-bar-track">
              <div className="preview-bar-fill violet-fill" style={{ width: '65%' }}></div>
            </div>
          </div>
          <div className="preview-bar-row">
            <div className="preview-bar-track">
              <div className="preview-bar-fill emerald-fill" style={{ width: '85%' }}></div>
            </div>
          </div>
        </div>
      );
    case 'sos':
      return (
        <div className="preview-content sos-preview" aria-hidden="true">
          <div className="sos-transmitter">
            <div className="sos-ring ring-1"></div>
            <div className="sos-ring ring-2"></div>
            <div className="sos-dot"></div>
          </div>
        </div>
      );
    default:
      return null;
  }
};
const Features = () => {
  return (
    <section className="features-section" id="features">
      <div className="features-container">
        {/* Section Header */}
        <header className="features-header">
          <span className="features-tag">Platform Features</span>
          <h2 className="features-title">Intelligent Guardrails</h2>
          <p className="features-subtitle">
            Integrated software algorithms and hardware nodes working concurrently to protect drivers.
          </p>
        </header>
        {/* Feature Cards Grid (4x2 on Desktop, 2x4 on Tablet, 1x8 on Mobile) */}
        <div className="features-grid">
          {FEATURES.map((feature) => (
            <article 
              key={feature.id} 
              className={`feature-card ${feature.id}-card`}
              tabIndex="0"
              role="region"
              aria-label={`${feature.title} feature card`}
              data-feature={feature.featureKey}
            >
              <div className="card-heading">
                <div className={`feature-icon-container ${feature.theme}`}>
                  <feature.icon size={20} aria-hidden="true" />
                </div>
                <h3 className="card-title">{feature.title}</h3>
              </div>
              
              <p className="card-description">{feature.description}</p>
              
              {/* Dynamic status hook for future live backend telemetry */}
              <div className="card-status-row">
                <span className="status-label">Status</span>
                <span className={`feature-status-text text-${feature.theme}`} data-status-label={feature.id}>
                  {feature.initialStatus}
                </span>
              </div>
              
              <div className="feature-preview">
                {renderPreview(feature.previewType)}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};
export default Features;
