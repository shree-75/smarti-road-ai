/**
 * @fileoverview AuthButton.jsx - Reusable Authentication Action Button
 * @module components/auth/AuthButton
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Render action triggers for form submits.
 * - Manage load/authenticating animation states.
 * - Enforce disable attributes when forms submit.
 * - Map to classes from Auth.css for native styling.
 * 
 * Exported APIs:
 * - AuthButton (Component)
 */

import React from 'react';
import '../../styles/Auth.css';

/**
 * Reusable Auth Form Submission Button.
 * 
 * @param {object} props - Component properties.
 * @param {string} props.children - Label text to show.
 * @param {boolean} [props.loading=false] - Whether to show a spinner/loading state.
 * @param {boolean} [props.disabled=false] - Disable trigger flag.
 * @param {string} [props.type='submit'] - Button trigger type.
 * @param {function} [props.onClick] - Trigger click handler callback.
 * @returns {React.JSX.Element} The AuthButton component.
 */
export const AuthButton = ({
  children,
  loading = false,
  disabled = false,
  type = 'submit',
  onClick,
  ...buttonProps
}) => {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className="form-button"
      {...buttonProps}
    >
      {loading ? (
        <>
          <div className="auth-loader" />
          <span>Authenticating...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
};
