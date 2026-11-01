/**
 * @fileoverview api.constants.js - Centralized API Constants and Configuration Parameters
 * @module constants/api
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Define HTTP request timeout bounds.
 * - Establish fallback API endpoint paths.
 * - Centralize all backend API route strings.
 * - Centralize standard HTTP header names.
 * 
 * Exported Constants:
 * - TIMEOUT_MS
 * - DEFAULT_API_URL
 * - HEADER_NAMES
 * - AUTH_ENDPOINTS
 * 
 * Dependencies:
 * - None
 */

/**
 * Global HTTP request timeout limit in milliseconds.
 * @type {number}
 */
export const TIMEOUT_MS = 10000;

/**
 * Fallback local API endpoint URL.
 * @type {string}
 */
export const DEFAULT_API_URL = 'http://127.0.0.1:8000/api/v1';

/**
 * Reusable HTTP header names.
 * @type {object}
 */
export const HEADER_NAMES = {
  AUTHORIZATION: 'Authorization',
  CONTENT_TYPE: 'Content-Type'
};

/**
 * Unified endpoint path mappings corresponding to FastAPI endpoints.
 * @type {object}
 */
export const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  VERIFY_EMAIL: '/auth/verify-email'
};
