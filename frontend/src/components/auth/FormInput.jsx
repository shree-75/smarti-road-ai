/**
 * @fileoverview FormInput.jsx - Standard Reusable Input Form Field
 * @module components/auth/FormInput
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Render an input field with label and error messages.
 * - Manage focus, accessibility states (aria properties), and keyboard input.
 * - Map to classes from Auth.css for native styling.
 * 
 * Exported APIs:
 * - FormInput (Component)
 */

import React from 'react';
import '../../styles/Auth.css';

/**
 * Standard Form Field Component.
 * 
 * @param {object} props - Component properties.
 * @param {string} props.id - Input field ID (matches html label for).
 * @param {string} props.label - User facing label.
 * @param {string} [props.type='text'] - Input type (email, text, etc.).
 * @param {string} props.value - Controlled input value string.
 * @param {function} props.onChange - Input value handler function.
 * @param {string} [props.error] - Field-level error validation message.
 * @param {string} [props.placeholder] - Help message to show in the field.
 * @param {boolean} [props.required=false] - Field required validation flag.
 * @returns {React.JSX.Element} The FormInput component.
 */
export const FormInput = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  error,
  placeholder,
  required = false,
  ...inputProps
}) => {
  const errorId = `${id}-error`;

  return (
    <div className="form-group">
      <label htmlFor={id} className="form-label">
        {label} {required && <span style={{ color: 'var(--color-rose, #f43f5e)' }}>*</span>}
      </label>
      
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? errorId : undefined}
        className="form-input"
        style={error ? { borderColor: 'var(--color-rose, #f43f5e)' } : {}}
        {...inputProps}
      />

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
