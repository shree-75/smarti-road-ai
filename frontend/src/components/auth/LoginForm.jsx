/**
 * @fileoverview LoginForm.jsx - Complete Interactive Login Form Component
 * @module components/auth/LoginForm
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Render email and password input elements.
 * - Enforce inline validation constraints using validation.js.
 * - Capture user login actions and delegate to AuthContext.
 * - Display friendly form-level API errors mapping from context using Auth.css styles.
 * 
 * Exported APIs:
 * - LoginForm (Component)
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';
import { validateEmail, validatePassword } from '../../utils/validation.js';
import { FormInput } from './FormInput.jsx';
import { PasswordInput } from './PasswordInput.jsx';
import { AuthButton } from './AuthButton.jsx';
import { ROUTE_PATHS } from '../../constants/routes.constants.js';
import '../../styles/Auth.css';

/**
 * LoginForm Component for user authentication.
 * 
 * @returns {React.JSX.Element} The LoginForm component.
 */
export const LoginForm = () => {
  const { login, authenticating, error: apiError } = useAuth();
  const navigate = useNavigate();

  // Field Inputs State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  // Field-level Validation Error State
  const [errors, setErrors] = useState({
    email: null,
    password: null
  });

  /**
   * Validates inputs and submits form credentials.
   * 
   * @async
   * @param {React.FormEvent} e - Form submit event.
   * @returns {Promise<void>}
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Run active validations
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);

    setErrors({
      email: emailValidation.error,
      password: passwordValidation.error
    });

    // Guard: Prevent submissions if checks fail
    if (!emailValidation.isValid || !passwordValidation.isValid) {
      return;
    }

    // Call global login action
    const res = await login(email, password);
    if (res.success) {
      navigate(ROUTE_PATHS.DASHBOARD);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="auth-form">
      {/* Global API Server Error Alert */}
      {apiError && (
        <div className="auth-alert auth-alert-error" role="alert">
          <div>
            <strong>Authentication Error: </strong>
            {apiError.message}
          </div>
        </div>
      )}

      {/* Email Field */}
      <FormInput
        id="email"
        label="Email Address"
        type="email"
        value={email}
        onChange={(e) => {
          setEmail(e.target.value);
          if (errors.email) {
            setErrors(prev => ({ ...prev, email: validateEmail(e.target.value).error }));
          }
        }}
        error={errors.email}
        placeholder="Enter your email"
        required
        disabled={authenticating}
        autoComplete="email"
      />

      {/* Password Field */}
      <PasswordInput
        id="password"
        label="Password"
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          if (errors.password) {
            setErrors(prev => ({ ...prev, password: validatePassword(e.target.value).error }));
          }
        }}
        error={errors.password}
        placeholder="Enter your password"
        required
        disabled={authenticating}
        autoComplete="current-password"
      />

      {/* Form Extra Options (Remember Me & Forgot Pass) */}
      <div 
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
          fontSize: '13px',
          fontFamily: 'var(--font-body)'
        }}
      >
        <label 
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--text-secondary, #9ca3af)',
            cursor: 'pointer',
            userSelect: 'none'
          }}
        >
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            disabled={authenticating}
            style={{ cursor: 'pointer' }}
          />
          Remember me
        </label>

        <Link to={ROUTE_PATHS.FORGOT_PASSWORD} className="auth-link">
          Forgot password?
        </Link>
      </div>

      {/* Action Submit Button */}
      <AuthButton loading={authenticating} disabled={authenticating}>
        Sign In
      </AuthButton>

      {/* Bottom redirection row */}
      <div className="auth-links-row" style={{ justifyContent: 'center' }}>
        <span style={{ fontSize: '13px', color: 'var(--text-secondary, #9ca3af)', fontFamily: 'var(--font-body)' }}>
          Don't have an account?{' '}
          <Link to={ROUTE_PATHS.REGISTER} className="auth-link" style={{ fontWeight: 600, color: 'var(--color-cyan, #06b6d4)' }}>
            Sign Up
          </Link>
        </span>
      </div>
    </form>
  );
};
