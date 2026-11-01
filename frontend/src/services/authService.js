/**
 * @fileoverview authService.js - Stateless Endpoint Wrapper for Auth APIs with Response Normalization
 * @module services/authService
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Define FastAPI backend authentication endpoints using centralized constants.
 * - Manage request payload serialization.
 * - Call API endpoints, normalize success/failure responses, and avoid propagating raw network errors.
 * 
 * Exported APIs:
 * - loginUser(email, password)
 * - registerUser(userData)
 * - logoutUser()
 * - refreshAccessToken()
 * - forgotPassword(email)
 * - resetPassword(token, password)
 * - verifyEmail(token)
 * - getCurrentUser()
 * 
 * Dependencies:
 * - api/axios
 * - constants/api.constants
 * - utils/errorMapper
 */

import { apiClient } from '../api/axios.js';
import { AUTH_ENDPOINTS } from '../constants/api.constants.js';
import { mapAuthError } from '../utils/errorMapper.js';

/**
 * Normalizes service function wrappers to return unified success/failure structures.
 * 
 * @async
 * @private
 * @template T
 * @param {function(): Promise<T>} apiCall - The async axios request function to execute.
 * @returns {Promise<{ success: boolean, data?: T, error?: { type: string, message: string } }>} The normalized response object.
 */
const executeRequest = async (apiCall) => {
  try {
    const responseData = await apiCall();
    return { success: true, data: responseData };
  } catch (error) {
    return { success: false, error: mapAuthError(error) };
  }
};

/**
 * Authenticates a user with the backend using email and password.
 * Formats request payload as URL-encoded form data as expected by FastAPI OAuth2 specs.
 * 
 * @param {string} email - The user's email address.
 * @param {string} password - The user's password.
 * @returns {Promise<object>} Normalized response containing success, data, and error fields.
 */
export const loginUser = (email, password) => {
  return executeRequest(async () => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post(AUTH_ENDPOINTS.LOGIN, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data;
  });
};

/**
 * Registers a new user account with the application.
 * 
 * @param {object} userData - Object containing email, password, and full name.
 * @returns {Promise<object>} Normalized response object.
 */
export const registerUser = (userData) => {
  return executeRequest(async () => {
    const response = await apiClient.post(AUTH_ENDPOINTS.REGISTER, userData);
    return response.data;
  });
};

/**
 * Performs server-side user logout, clearing cookies.
 * 
 * @returns {Promise<object>} Normalized response object.
 */
export const logoutUser = () => {
  return executeRequest(async () => {
    const response = await apiClient.post(AUTH_ENDPOINTS.LOGOUT);
    return response.data;
  });
};

/**
 * Requests a new access token using the HTTP-only refresh cookie.
 * 
 * @returns {Promise<object>} Normalized response object.
 */
export const refreshAccessToken = () => {
  return executeRequest(async () => {
    const response = await apiClient.post(AUTH_ENDPOINTS.REFRESH);
    return response.data;
  });
};

/**
 * Sends a request to send a password reset recovery email link.
 * 
 * @param {string} email - User email address.
 * @returns {Promise<object>} Normalized response object.
 */
export const forgotPassword = (email) => {
  return executeRequest(async () => {
    const response = await apiClient.post(AUTH_ENDPOINTS.FORGOT_PASSWORD, { email });
    return response.data;
  });
};

/**
 * Submits password reset code and sets a new account password.
 * 
 * @param {string} token - Security verification code.
 * @param {string} password - New password value.
 * @returns {Promise<object>} Normalized response object.
 */
export const resetPassword = (token, password) => {
  return executeRequest(async () => {
    const response = await apiClient.post(AUTH_ENDPOINTS.RESET_PASSWORD, { token, password });
    return response.data;
  });
};

/**
 * Validates a user's signup email confirmation token.
 * 
 * @param {string} token - Verification token parameter.
 * @returns {Promise<object>} Normalized response object.
 */
export const verifyEmail = (token) => {
  return executeRequest(async () => {
    const response = await apiClient.get(`${AUTH_ENDPOINTS.VERIFY_EMAIL}?token=${encodeURIComponent(token)}`);
    return response.data;
  });
};

/**
 * Retrieves the currently authenticated profile information from the server.
 * 
 * @returns {Promise<object>} Normalized response object.
 */
export const getCurrentUser = () => {
  return executeRequest(async () => {
    const response = await apiClient.get(AUTH_ENDPOINTS.ME);
    return response.data;
  });
};
