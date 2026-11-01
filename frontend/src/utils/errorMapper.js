/**
 * @fileoverview errorMapper.js - Standardized Error Mapping Utility for Auth Exceptions
 * @module utils/errorMapper
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Accept raw HTTP/Axios or local JavaScript exceptions.
 * - Translate raw exceptions into standardized { type, message } objects.
 * - Ensure zero unhandled mapping exceptions.
 * 
 * Exported APIs:
 * - mapAuthError(error)
 * 
 * Dependencies:
 * - constants/auth.constants
 */

import { ERROR_CATEGORIES } from '../constants/auth.constants.js';

/**
 * Translates a raw catch exception/AxiosError into a normalized client error structure.
 * 
 * @param {any} error - The caught error object.
 * @returns {object} Standardized error structure: { type: string, message: string }.
 */
export const mapAuthError = (error) => {
  if (!error) {
    return {
      type: ERROR_CATEGORIES.UNKNOWN_ERROR,
      message: 'An unknown error occurred. Please try again.'
    };
  }

  // Handle explicit request timeouts / aborts
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return {
      type: ERROR_CATEGORIES.REQUEST_TIMEOUT,
      message: 'The request timed out. Please check your connection and try again.'
    };
  }

  // Handle network disconnection or server unreachable
  if (!error.response) {
    return {
      type: ERROR_CATEGORIES.NETWORK_ERROR,
      message: 'Unable to connect to the server. Please verify your internet connection.'
    };
  }

  const status = error.response.status;
  const serverDetail = error.response.data?.detail || error.response.data?.message;

  switch (status) {
    case 400:
    case 401:
      return {
        type: ERROR_CATEGORIES.INVALID_CREDENTIALS,
        message: serverDetail || 'Invalid credentials. Please verify your email and password.'
      };
    case 403:
      return {
        type: ERROR_CATEGORIES.UNKNOWN_ERROR,
        message: serverDetail || 'Access denied: You are not authorized to perform this operation.'
      };
    case 500:
      return {
        type: ERROR_CATEGORIES.SERVER_ERROR,
        message: 'An internal server error occurred. Please try again later.'
      };
    default:
      return {
        type: ERROR_CATEGORIES.UNKNOWN_ERROR,
        message: serverDetail || 'An unexpected authentication exception occurred.'
      };
  }
};
