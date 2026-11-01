/**
 * @fileoverview auth.constants.js - Authentication State and Error Classification Constants
 * @module constants/auth
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Define standard user-facing error classification categories.
 * 
 * Exported Constants:
 * - ERROR_CATEGORIES
 * 
 * Dependencies:
 * - None
 */

/**
 * Standardized Authentication Error Classification Categories.
 * Consumed globally by services and UI handlers to present localized states messages.
 * @type {object}
 */
export const ERROR_CATEGORIES = {
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  SESSION_EXPIRED: 'SESSION_EXPIRED',
  NETWORK_ERROR: 'NETWORK_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  REQUEST_TIMEOUT: 'REQUEST_TIMEOUT',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};
