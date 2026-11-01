/**
 * @fileoverview PublicRoute.jsx - Route Guard to Redirect Authenticated Users
 * @module components/auth/PublicRoute
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Read global auth state via useAuth custom hook.
 * - Hold view rendering while the session is initializing.
 * - Redirect authenticated users attempting to access guest-only pages (e.g. login/register) to dashboard.
 * - Render child page content or routing outlet if user is unauthenticated guest.
 * 
 * Exported APIs:
 * - PublicRoute (Component)
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
 * Router container filtering public auth views (like login) from logged-in members.
 * Suspend routing actions until session credentials loading wraps.
 * 
 * @param {object} props - Component properties.
 * @param {React.ReactNode} [props.children] - Nested route layout view component.
 * @returns {React.JSX.Element|null} Navigation redirect or target view content.
 */
export const PublicRoute = ({ children }) => {
  const { isAuthenticated, initializing } = useAuth();

  // Suspends all route evaluation and displays loading indicators during initializations checks
  if (initializing) {
    return <LoadingScreen message="Initializing session details..." fullscreen={true} size="large" />;
  }

  // Redirect authenticated users to the main dashboard page
  if (isAuthenticated) {
    return <Navigate to={ROUTE_PATHS.DASHBOARD} replace />;
  }

  // Render children if provided, otherwise render default Outlet
  return children ? children : <Outlet />;
};
