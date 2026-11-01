/**
 * @fileoverview token.js - Client-Side In-Memory JWT Management Utilities
 * @module utils/token
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Hold and manage client JWT Access Token securely in-memory.
 * - Provide getter, setter, and remover methods for the token.
 * - Safely decode JWT payloads without throwing exceptions.
 * - Verify JWT expiration based on client system epoch time.
 * 
 * Exported APIs:
 * - setAccessToken(token)
 * - getAccessToken()
 * - removeAccessToken()
 * - decodeToken(token)
 * - isTokenExpired(token)
 * 
 * Dependencies:
 * - None (Native Standard Web APIs only)
 */

/**
 * Private in-memory store for the JWT Access Token.
 * Prefixed with underscore to signify module-private scope.
 * @type {string|null}
 * @private
 */
let _accessToken = null;

/**
 * Sets the active access token in the application memory.
 * 
 * @param {string|null} token - The raw JWT access token to store, or null to clear.
 * @returns {void}
 * @example
 * setAccessToken("eyJhbGciOi...");
 */
export const setAccessToken = (token) => {
  if (token === null || typeof token === 'string') {
    _accessToken = token;
  }
};

/**
 * Retrieves the stored access token from the application memory.
 * 
 * @returns {string|null} The stored JWT access token, or null if not set.
 * @example
 * const token = getAccessToken();
 */
export const getAccessToken = () => {
  return _accessToken;
};

/**
 * Clears the stored access token from the application memory.
 * 
 * @returns {void}
 * @example
 * removeAccessToken();
 */
export const removeAccessToken = () => {
  _accessToken = null;
};

/**
 * Safely decodes a JWT payload without verifying its signature.
 * Returns null if the token structure is malformed or invalid.
 * 
 * @param {string} token - The raw JWT token string to decode.
 * @returns {object|null} The decoded JSON payload object, or null if invalid/malformed.
 * @example
 * const payload = decodeToken("eyJhbGciOi...");
 */
export const decodeToken = (token) => {
  if (!token || typeof token !== 'string') {
    return null;
  }

  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payloadPart = parts[1];
    // Replace URL-safe base64 characters with standard base64 characters
    const normalizedBase64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    
    // Decode base64 bytes safely and handle unicode characters properly
    const decodedString = decodeURIComponent(
      atob(normalizedBase64)
        .split('')
        .map((char) => '%' + ('00' + char.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(decodedString);
  } catch (_error) {
    // Zero-Exception Policy: Suppress any parse errors and return null
    return null;
  }
};

/**
 * Evaluates if a JWT token is expired compared to the current system epoch time.
 * Returns true if expired, invalid, or missing the 'exp' claim.
 * 
 * @param {string} token - The raw JWT token string to check.
 * @returns {boolean} True if token is expired or invalid; false otherwise.
 * @example
 * const expired = isTokenExpired("eyJhbGciOi...");
 */
export const isTokenExpired = (token) => {
  if (!token || typeof token !== 'string') {
    return true;
  }

  const payload = decodeToken(token);
  if (!payload || typeof payload.exp !== 'number') {
    return true;
  }

  const currentEpochSeconds = Math.floor(Date.now() / 1000);
  return payload.exp < currentEpochSeconds;
};