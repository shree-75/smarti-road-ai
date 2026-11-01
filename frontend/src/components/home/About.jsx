import React from 'react';
import { Cpu, ShieldCheck, Network, Eye, Server, Layout, BellRing } from 'lucide-react';
import './About.css';

// Core pillars constant array declared outside component function
const ABOUT_PILLARS = [
  {
    id: 'edge-intelligence',
    icon: Cpu,
    title: 'Edge Intelligence',
    description: 'All computer vision calculations run locally on dedicated hardware for sub-100ms response times without internet dependencies.'
  },
  {
    id: 'biometric-privacy',
    icon: ShieldCheck,
    title: 'Biometric Privacy',
    description: 'Strict volatile data processing. Gaze matrices and facial coordinates are processed in memory and instantly discarded.'
  },
  {
    id: 'iot-sensor-mesh',
    icon: Network,
    title: 'IoT Sensor Mesh',
    description: 'Plug-and-play integration checks compatibility with standard vehicle telemetry, G-force accelerometers, and biometric sensors.'
  }
];

// Tech stack items mapping Categories
const TECH_STACK = [
  { name: 'React', category: 'Frontend' },
  { name: 'FastAPI', category: 'Backend' },
  { name: 'OpenCV', category: 'AI Vision' },
  { name: 'MediaPipe', category: 'AI Vision' },
  { name: 'ESP32', category: 'Hardware' },
  { name: 'MAX30102', category: 'Biometrics' },
  { name: 'MQ-Series', category: 'Sensor' },
  { name: 'MQTT', category: 'Relay' }
];

// Pipeline nodes mapping data flow sequence
const PIPELINE_NODES = [
  {
    id: 'sensors',
    icon: Eye,
    label: 'Camera / Sensors',
    sublabel: 'Biometric & Video Inputs',
    theme: 'cyan'
  },
  {
    id: 'esp32',
    icon: Cpu,
    label: 'ESP32 Edge Node',
    sublabel: 'Local Hardware Aggregation',
    theme: 'violet'
  },
  {
    id: 'fastapi',
    icon: Server,
    label: 'FastAPI Backend',
    sublabel: 'WebSocket Server Relay',
    theme: 'cyan'
  },
  {
    id: 'dashboard',
    icon: Layout,
    label: 'React Dashboard',
    sublabel: 'Live Telemetry Interface',
    theme: 'violet'
  },
  {
    id: 'sos',
    icon: BellRing,
    label: 'Emergency SOS',
    sublabel: 'Active Alert Dispatch',
    theme: 'emerald'
  }
];

const About = () => {
  return (
    <section className="about-section" id="about">
      <div className="about-container">
        {/* Left Side Column: Vision, Mission & Tech Pillars */}
        <div className="about-content">
          <header className="about-badge-wrapper">
            <span className="about-tag-badge">Mission & Pillars</span>
          </header>

          <h2 className="about-title">Why SmartRoad AI</h2>

          <p className="about-paragraph">
            Traditional telematics and dashcams only record logs reactive to collisions. Cloud-based safety tools fail in remote regions with poor signal coverage, while continuous camera uploads compromise operator privacy. SmartRoad AI processes all parameters locally in volatile memory, protecting both safety and privacy in real time.
          </p>

          <div className="about-vision-block">
            <h3 className="vision-header">Project Vision</h3>
            <p className="vision-text">
              To establish a latency-free, privacy-preserving intelligent vehicle safety mesh. By deploying locally processed Edge AI guardrails, we aim to prevent driver errors and coordinate instantaneous, automatic emergency response routes without relying on cellular availability or cloud dependencies.
            </p>
          </div>

          {/* Core Pillars Grid */}
          <div className="about-pillars-list">
            {ABOUT_PILLARS.map((pillar) => (
              <article 
                key={pillar.id} 
                className="pillar-item"
                tabIndex="0"
                role="region"
                aria-label={`${pillar.title} pillar`}
              >
                <div className="pillar-header">
                  <div className="pillar-icon-container">
                    <pillar.icon size={18} aria-hidden="true" />
                  </div>
                  <h4 className="pillar-title">{pillar.title}</h4>
                </div>
                <p className="pillar-description">{pillar.description}</p>
              </article>
            ))}
          </div>
        </div>

        {/* Right Side Column: Data Flow Architecture Mockup (HTML/CSS only) */}
        <div className="about-visual">
          <div className="architecture-mockup">
            <div className="architecture-header">
              <span className="mockup-dot"></span>
              <span className="mockup-title">SYSTEM FLOW DIAGRAM</span>
            </div>

            <div className="pipeline-container">
              {/* Continuous SVG Flow Connector Line */}
              <svg className="pipeline-line" viewBox="0 0 20 400" preserveAspectRatio="none" aria-hidden="true">
                <line x1="10" y1="0" x2="10" y2="400" className="line-bg" />
                <line x1="10" y1="0" x2="10" y2="400" className="line-flow" />
              </svg>

              <div className="pipeline-nodes-list">
                {PIPELINE_NODES.map((node) => (
                  <div 
                    key={node.id} 
                    className={`pipeline-node-card ${node.theme}-theme`}
                    data-node={node.id}
                    tabIndex="0"
                    role="region"
                    aria-label={`Pipeline step: ${node.label}, ${node.sublabel}`}
                  >
                    <div className="node-icon-wrapper">
                      <node.icon size={18} aria-hidden="true" />
                    </div>
                    <div className="node-content">
                      <div className="node-label">{node.label}</div>
                      <div className="node-sublabel">{node.sublabel}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;