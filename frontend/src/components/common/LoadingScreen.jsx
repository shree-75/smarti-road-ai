/**
 * @fileoverview LoadingScreen.jsx - Reusable Loading Overlay/Spinner Component
 * @module components/common/LoadingScreen
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Render a visually premium spinner/loading layout.
 * - Accept message, fullscreen, and size configuration props.
 * - Reuse Auth.css or variables.css styles.
 * 
 * Exported APIs:
 * - LoadingScreen (Component)
 */

import React from 'react';

/**
 * Reusable Loading Spinner Component.
 * Supports different sizes and fullscreen overlay positioning.
 * 
 * @param {object} props - React props.
 * @param {string} [props.message='Loading secure session...'] - Label text to show.
 * @param {boolean} [props.fullscreen=true] - Whether to show as a full screen viewport overlay.
 * @param {string} [props.size='medium'] - Spinner size: 'small' | 'medium' | 'large'.
 * @returns {React.JSX.Element} The LoadingScreen component.
 */
export const LoadingScreen = ({ 
  message = 'Loading secure session...', 
  fullscreen = true, 
  size = 'medium' 
}) => {
  const containerStyle = fullscreen 
    ? {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        width: '100vw',
        position: 'fixed',
        top: 0,
        left: 0,
        backgroundColor: 'var(--color-bg, #0b0f19)',
        zIndex: 9999,
        color: 'var(--color-text, #f3f4f6)',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }
    : {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '2rem',
        color: 'var(--color-text, #f3f4f6)',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      };

  const spinnerSize = size === 'small' ? '24px' : size === 'large' ? '64px' : '40px';

  return (
    <div className="loading-screen-container" style={containerStyle}>
      <div 
        className="loading-spinner" 
        style={{
          width: spinnerSize,
          height: spinnerSize,
          border: '3px solid rgba(255, 255, 255, 0.1)',
          borderTop: '3px solid var(--color-primary, #3b82f6)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '1rem'
        }}
      />
      {message && <p style={{ margin: 0, fontSize: '0.95rem', opacity: 0.8 }}>{message}</p>}
      
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
