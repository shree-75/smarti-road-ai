/**
 * @fileoverview PasswordInput.jsx - Reusable Password Input Field with Show/Hide Toggle
 * @module components/auth/PasswordInput
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Render secure password input fields.
 * - Toggle password visibility between dots and plaintext.
 * - Support accessibility attributes and error layouts.
 * - Map to classes from Auth.css for native styling.
 * 
 * Exported APIs:
 * - PasswordInput (Component)
 */

import React, { useState } from 'react';
import '../../styles/Auth.css';

/**
 * Reusable Password Field with visibility controls.
 * 
 * @param {object} props - Component properties.
 * @param {string} props.id - Input field ID.
 * @param {string} props.label - User facing label.
 * @param {string} props.value - Controlled input value.
 * @param {function} props.onChange - Input value handler function.
 * @param {string} [props.error] - Field-level validation error message.
 * @param {string} [props.placeholder='••••••••'] - Help placeholder string.
 * @param {boolean} [props.required=false] - Field required validation flag.
 * @returns {React.JSX.Element} The PasswordInput component.
 */
export const PasswordInput = ({
  id,
  label,
  value,
  onChange,
  error,
  placeholder = '••••••••',
  required = false,
  ...inputProps
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const errorId = `${id}-error`;

  const toggleVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className="form-group">
      <label htmlFor={id} className="form-label">
        {label} {required && <span style={{ color: 'var(--color-rose, #f43f5e)' }}>*</span>}
      </label>
      
      <div className="password-input-wrapper" style={{ position: 'relative', width: '100%' }}>
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? errorId : undefined}
          className="form-input"
          style={{
            paddingRight: '48px',
            borderColor: error ? 'var(--color-rose, #f43f5e)' : undefined
          }}
          {...inputProps}
        />
        
        <button
          type="button"
          onClick={toggleVisibility}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          style={{
            position: 'absolute',
            right: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary, #9ca3af)',
            cursor: 'pointer',
            padding: '4px',
            fontSize: '12px',
            fontFamily: 'var(--font-body)',
            outline: 'none',
            userSelect: 'none'
          }}
        >
          {showPassword ? 'Hide' : 'Show'}
        </button>
      </div>

      {error && (
        <span 
          id={errorId} 
          role="alert"
          style={{
            display: 'block',
            marginTop: '4px',
            fontSize: '11.5px',
            color: 'var(--color-rose, #f43f5e)',
            fontFamily: 'var(--font-body)'
          }}
        >
          {error}
        </span>
      )}
    </div>
  );
};
