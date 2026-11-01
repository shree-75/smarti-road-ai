/**
 * @fileoverview Register.jsx - User Sign-up Page Component (Placeholder)
 * @module pages/Register
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 */

import React from 'react';
import { AuthLayout } from '../components/auth/AuthLayout.jsx';
import { RegisterForm } from '../components/auth/RegisterForm.jsx';

export const Register = () => {
  return (
    <AuthLayout 
      title="Create Account" 
      subtitle="Sign up for SmartRoad AI analytics and driver tracking."
    >
      <RegisterForm />
    </AuthLayout>
  );
};

export default Register;
