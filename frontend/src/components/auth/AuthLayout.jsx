/**
 * @fileoverview AuthLayout.jsx - Reusable Layout Wrapper for Authentication Pages
 * @module components/auth/AuthLayout
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Wrap authentication form panels (login, register).
 * - Render branding elements (SmartRoad AI logotype, description).
 * - Implement premium glassmorphic visual styles via Auth.css classes.
 * 
 * Exported APIs:
 * - AuthLayout (Component)
 */

import React from 'react';
import '../../styles/Auth.css';

/**
 * Common layout panel wrapping authentication views with consistent branding and styling.
 * 
 * @param {object} props - Component properties.
 * @param {React.ReactNode} props.children - Child nodes representing the login form, etc.
 * @param {string} [props.title] - Title heading.
 * @param {string} [props.subtitle] - Subtitle description.
 * @returns {React.JSX.Element} The AuthLayout component.
 */
export const AuthLayout = ({ children, title, subtitle }) => {
  return (
    <div className="auth-layout">
      {/* Reusable Glassmorphism Card */}
      <div className="auth-card">
        {/* Brand Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <span className="auth-logo-icon" style={{ fontSize: '1.5rem' }}>🚗</span>
            <span className="auth-logo-text">
              SmartRoad <span className="highlight">AI</span>
            </span>
          </div>
          {title && <h2 className="auth-title">{title}</h2>}
          {subtitle && <p className="auth-subtitle">{subtitle}</p>}
        </div>

        {/* Form Content */}
        {children}
      </div>
    </div>
  );
};
