/**
 * @fileoverview AuthContext.jsx - Global React Context Provider for Authentication State
 * @module context/AuthContext
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Hold and coordinate global React authentication state (currentUser, isAuthenticated).
 * - Distinguish loading states between initializing and authenticating.
 * - Consume normalized API responses from authService.
 * - Perform silent refresh token operations on application load.
 * - Enforce client cleanup on session logout regardless of server state.
 * 
 * Exported APIs:
 * - AuthProvider (Component)
 * - useAuth() (Custom hook)
 * 
 * Dependencies:
 * - React
 * - services/authService
 * - utils/token
 * - constants/auth.constants
 */

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { loginUser, logoutUser, refreshAccessToken, getCurrentUser } from '../services/authService.js';
import { setAccessToken, removeAccessToken, decodeToken } from '../utils/token.js';
import { ERROR_CATEGORIES } from '../constants/auth.constants.js';

/**
 * Core authentication context instance.
 * @private
 */
const AuthContext = createContext(null);

/**
 * Provider component wrapping the React app to provide authentication context.
 * 
 * @param {object} props - Component properties.
 * @param {React.ReactNode} props.children - Child elements to wrap.
 * @returns {React.JSX.Element} AuthContext Provider component.
 */
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [authenticating, setAuthenticating] = useState(false);
  const [error, setError] = useState(null);

  // Maintain reference to authentication state to prevent stale closure loops in callback dependency trees
  const isAuthenticatedRef = useRef(isAuthenticated);
  useEffect(() => {
    isAuthenticatedRef.current = isAuthenticated;
  }, [isAuthenticated]);

  /**
   * Fetches the current user profile from the server using the active access token.
   * Consumed to load full profile details after login or session refresh.
   * 
   * @async
   * @returns {Promise<object|null>} The user profile object, or null if unauthorized.
   */
  const fetchUserProfile = useCallback(async () => {
    const res = await getCurrentUser();
    if (res.success) {
      setCurrentUser(res.data);
      setIsAuthenticated(true);
      return res.data;
    }
    return null;
  }, []);

  /**
   * Dispatches a silent token refresh check to restore active sessions on start.
   * Runs automatically on mounting.
   * 
   * @async
   * @returns {Promise<void>}
   */
  const refreshSession = useCallback(async () => {
    // Proactive Guard: Avoid redundant refresh calls if session is already authenticated
    if (isAuthenticatedRef.current) {
      setInitializing(false);
      return;
    }

    try {
      setError(null);
      const res = await refreshAccessToken();
      
      if (res.success && res.data?.access_token) {
        setAccessToken(res.data.access_token);
        const decoded = decodeToken(res.data.access_token);
        setCurrentUser(decoded);
        setIsAuthenticated(true);
        await fetchUserProfile();
      } else {
        removeAccessToken();
        setCurrentUser(null);
        setIsAuthenticated(false);
      }
    } catch (err) {
      removeAccessToken();
      setCurrentUser(null);
      setIsAuthenticated(false);
      
      // If client was previously registered as authenticated, raise session expiry error
      if (isAuthenticatedRef.current) {
        setError({
          type: ERROR_CATEGORIES.SESSION_EXPIRED,
          message: 'Your session has expired. Please sign in again.'
        });
      }
    } finally {
      setInitializing(false);
    }
  }, [fetchUserProfile]);

  /**
   * Authenticates user using email and password, caches tokens, and initializes profiles.
   * 
   * @async
   * @param {string} email - Account login email address.
   * @param {string} password - Account password input.
   * @returns {Promise<{ success: boolean, error?: object }>} Result of the login attempt.
   */
  const login = useCallback(async (email, password) => {
    setAuthenticating(true);
    setError(null);
    try {
      const res = await loginUser(email, password);
      
      if (res.success && res.data?.access_token) {
        setAccessToken(res.data.access_token);
        const decoded = decodeToken(res.data.access_token);
        setCurrentUser(decoded);
        setIsAuthenticated(true);
        await fetchUserProfile();
        return { success: true };
      } else {
        const mappedError = res.error || {
          type: ERROR_CATEGORIES.UNKNOWN_ERROR,
          message: 'Login failed: Authentication token is missing.'
        };
        setError(mappedError);
        return { success: false, error: mappedError };
      }
    } catch (err) {
      const fallbackErr = {
        type: ERROR_CATEGORIES.UNKNOWN_ERROR,
        message: 'An unexpected error occurred during login.'
      };
      setError(fallbackErr);
      return { success: false, error: fallbackErr };
    } finally {
      setAuthenticating(false);
    }
  }, [fetchUserProfile]);

  /**
   * Resets client sessions, deletes memory caches, and revokes refresh cookies on backend.
   * 
   * @async
   * @returns {Promise<void>}
   */
  const logout = useCallback(async () => {
    setAuthenticating(true);
    setError(null);
    try {
      await logoutUser();
    } catch (err) {
      console.warn('Backend session revocation failed on logout:', err);
    } finally {
      removeAccessToken();
      setCurrentUser(null);
      setIsAuthenticated(false);
      setAuthenticating(false);
    }
  }, []);

  // Execute mounting session restorations
  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  // Memoize values container to optimize component renders tree
  const contextValue = useMemo(() => ({
    currentUser,
    isAuthenticated,
    initializing,
    authenticating,
    error,
    login,
    logout,
    refreshSession
  }), [
    currentUser,
    isAuthenticated,
    initializing,
    authenticating,
    error,
    login,
    logout,
    refreshSession
  ]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom React hook accessing global authentication values securely.
 * 
 * @returns {object} Context actions and states mapping.
 * @throws {Error} If consumed outside of the AuthProvider.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be consumed within an AuthProvider container.');
  }
  return context;
};

export default AuthContext;