/**
 * @fileoverview ProtectedRoute.jsx - Route Guard to Restrict Guest Access
 * @module components/auth/ProtectedRoute
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Read global auth state via useAuth custom hook.
 * - Hold view rendering while the session is initializing.
 * - Redirect unauthenticated users to the login route path.
 * - Render private content children or routing outlet on success.
 * 
 * Exported APIs:
 * - ProtectedRoute (Component)
 * 
 * Dependencies:
 * - React
 * - react-router-dom
 * - context/AuthContext
 */

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';
import { LoadingScreen } from '../common/LoadingScreen.jsx';
import { ROUTE_PATHS } from '../../constants/routes.constants.js';

/**
 * Router container guarding private child layouts from unauthenticated access.
 * Suspend routing actions until session credentials loading wraps.
 * 
 * @param {object} props - Component properties.
 * @param {React.ReactNode} [props.children] - Nested route layout view component.
 * @returns {React.JSX.Element|null} Navigation redirect or target view content.
 */
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, initializing } = useAuth();

  // Suspends all route evaluation and displays loading indicators during initializations checks
  if (initializing) {
    return <LoadingScreen message="Accessing protected dashboard..." fullscreen={true} size="large" />;
  }

  // Redirect guest users back to login page
  if (!isAuthenticated) {
    return <Navigate to={ROUTE_PATHS.LOGIN} replace />;
  }

  // Render children if provided, otherwise render default Outlet
  return children ? children : <Outlet />;
};
