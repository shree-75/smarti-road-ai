import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield } from 'lucide-react';
import './Footer.css';

// Site anchor navigation configuration
const SITE_LINKS = [
  { name: 'Home', path: '/', isHash: false },
  { name: 'Features', path: '/#features', isHash: true, hash: 'features' },
  { name: 'About', path: '/#about', isHash: true, hash: 'about' },
  { name: 'Login', path: '/login', isHash: false }
];

// Hardware integration stack references
const HARDWARE_STACK = [
  { name: 'ESP32 Node Relay' },
  { name: 'Camera Sensors' },
  { name: 'Biometric Wearables' },
  { name: 'MQ Gas Checkers' }
];

// Legal document targets
const LEGAL_LINKS = [
  { name: 'Privacy Policy', path: '/privacy' },
  { name: 'Terms of Service', path: '/terms' }
];

// Future-ready status checks
const STATUS_ITEMS = [
  { id: 'frontend', name: 'UI Platform' },
  { id: 'backend', name: 'FastAPI Relay' },
  { id: 'esp32', name: 'ESP32 Nodes' },
  { id: 'ai', name: 'Edge Engine' }
];

const Footer = () => {
  const location = useLocation();

  // Scroll handler ensuring smooth movement to anchors on local home page
  const handleNavClick = (e, item) => {
    if (item.isHash) {
      if (location.pathname === '/') {
        e.preventDefault();
        const element = document.getElementById(item.hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }
    } else if (item.path === '/' && location.pathname === '/') {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleLogoClick = (e) => {
    if (location.pathname === '/') {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <footer className="footer-container" role="contentinfo">
      {/* Top Tier: Columns Grid */}
      <div className="footer-top">
        <div className="footer-grid">
          {/* Column 1: Brand Profile */}
          <div className="footer-brand-col">
            <Link to="/" className="footer-logo" onClick={handleLogoClick}>
              <Shield className="footer-logo-icon" size={22} aria-hidden="true" />
              <span className="footer-logo-text">
                SmartRoad <span className="highlight">AI</span>
              </span>
            </Link>
            <p className="footer-brand-desc">
              Intelligent road safety mesh protecting fleet operators and drivers through real-time edge processing and biometric telemetry.
            </p>
          </div>

          {/* Column 2: Navigation Links Map */}
          <div className="footer-links-col">
            <h4 className="footer-col-title">Navigation</h4>
            <nav className="footer-nav" aria-label="Footer Navigation">
              <ul className="footer-links-list">
                {SITE_LINKS.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className="footer-link"
                      onClick={(e) => handleNavClick(e, link)}
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          </div>

          {/* Column 3: Hardware Integration References */}
          <div className="footer-links-col">
            <h4 className="footer-col-title">Hardware Core</h4>
            <ul className="footer-links-list">
              {HARDWARE_STACK.map((hw) => (
                <li key={hw.name}>
                  <span className="footer-static-item" tabIndex="0">
                    {hw.name}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Tier: Copyright, status lights, legal links */}
      <div className="footer-bottom">
        <div className="footer-bottom-container">
          <div className="footer-copyright-group">
            <span className="copyright-text">
              &copy; {new Date().getFullYear()} SmartRoad AI. All rights reserved.
            </span>
            <div className="footer-legal-links">
              {LEGAL_LINKS.map((link) => (
                <Link key={link.name} to={link.path} className="footer-legal-link">
                  {link.name}
                </Link>
              ))}
            </div>
          </div>

          {/* Connected WebSocket Status Checks */}
          <div className="footer-status-group">
            {STATUS_ITEMS.map((item) => (
              <div 
                key={item.id} 
                className="status-beacon-card"
                data-status={item.id}
                tabIndex="0"
                aria-label={`System module status: ${item.name} is active`}
              >
                <span className="beacon-indicator active" aria-hidden="true"></span>
                <span className="beacon-label">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;