/**
 * @fileoverview Login.jsx - User Sign-in Page Component
 * @module pages/Login
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Render user sign-in page.
 * - Wrap authentication form inside standard branding layout card.
 * 
 * Exported APIs:
 * - Login (Component)
 */

import React from 'react';
import { AuthLayout } from '../components/auth/AuthLayout.jsx';
import { LoginForm } from '../components/auth/LoginForm.jsx';

/**
 * Login Page Component.
 * 
 * @returns {React.JSX.Element} The Login component.
 */
export const Login = () => {
  return (
    <AuthLayout 
      title="Welcome Back" 
      subtitle="Sign in to monitor road safety & analytics in real time."
    >
      <LoginForm />
    </AuthLayout>
  );
};

export default Login;
