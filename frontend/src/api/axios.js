/**
 * @fileoverview axios.js - Global Shared Axios HTTP Client with Promise-Shared Auto-Refresh Interceptors
 * @module api/axios
 * @version 2.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Initialize the global Axios instance with environment-based configuration.
 * - Inject in-memory access tokens dynamically into outgoing request headers.
 * - Catch 401 response errors and execute a single silent token refresh retry.
 * - Share a single refresh promise across concurrent 401 failures to prevent multiple refresh calls.
 * - Clear local token memory and fail requests if refresh tokens are invalid.
 * 
 * Exported APIs:
 * - apiClient (AxiosInstance)
 * 
 * Dependencies:
 * - axios
 * - utils/token
 * - constants/api.constants
 */

import axios from 'axios';
import { getAccessToken, setAccessToken, removeAccessToken } from '../utils/token.js';
import { AUTH_ENDPOINTS, TIMEOUT_MS, HEADER_NAMES, DEFAULT_API_URL } from '../constants/api.constants.js';

/**
 * Resolves the API base URL safely, supporting both Vite env variables and Node.js testing.
 * @returns {string} The base URL.
 */
const resolveBaseUrl = () => {
  try {
    return import.meta.env.VITE_API_URL || DEFAULT_API_URL;
  } catch (_e) {
    return DEFAULT_API_URL;
  }
};

/**
 * Configured API client instance for HTTP communication.
 * Sets credentials to true to automatically forward secure refresh cookies.
 */
export const apiClient = axios.create({
  baseURL: resolveBaseUrl(),
  timeout: TIMEOUT_MS,
  withCredentials: true,
  headers: {
    [HEADER_NAMES.CONTENT_TYPE]: 'application/json'
  }
});

/**
 * Shared promise container for ongoing token refresh operations.
 * Prevents concurrent API failures from dispatching redundant token refreshes.
 * @type {Promise<string>|null}
 */
let _refreshPromise = null;

// Outgoing Request Interceptor: Attach bearer tokens from in-memory cache
apiClient.interceptors.request.use(
  (config) => {
    // Standard request AbortController support hook
    if (!config.signal) {
      const controller = new AbortController();
      config.signal = controller.signal;
    }

    const token = getAccessToken();
    if (token && config.headers) {
      config.headers[HEADER_NAMES.AUTHORIZATION] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Incoming Response Interceptor: Handles expired access tokens and runs silent retries
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Guard 1: Verify if the request was intentionally aborted/cancelled
    if (axios.isCancel(error)) {
      return Promise.reject(error);
    }

    // Guard 2: Verify response exists and is unauthorized, and request is retryable
    if (!error.response || error.response.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    // Guard 3: If the request failed on login, refresh, or logout endpoints, do not attempt to refresh
    const requestUrl = originalRequest.url || '';
    if (
      requestUrl.includes(AUTH_ENDPOINTS.LOGIN) ||
      requestUrl.includes(AUTH_ENDPOINTS.REFRESH) ||
      requestUrl.includes(AUTH_ENDPOINTS.LOGOUT)
    ) {
      if (!requestUrl.includes(AUTH_ENDPOINTS.LOGIN)) {
        removeAccessToken();
      }
      return Promise.reject(error);
    }

    // Guard 4: Prevent infinite loops by checking the retry flag
    if (originalRequest._retry) {
      removeAccessToken();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    // Implement Promise-Sharing Retry Strategy to resolve concurrent 401 collisions
    if (!_refreshPromise) {
      _refreshPromise = apiClient
        .post(AUTH_ENDPOINTS.REFRESH, {}, { timeout: TIMEOUT_MS })
        .then((refreshResponse) => {
          const newAccessToken = refreshResponse.data?.access_token;
          if (!newAccessToken) {
            throw new Error('Refresh failed: Missing new access token in response.');
          }
          setAccessToken(newAccessToken);
          return newAccessToken;
        })
        .catch((refreshError) => {
          removeAccessToken();
          throw refreshError;
        })
        .finally(() => {
          _refreshPromise = null;
        });
    }

    try {
      const token = await _refreshPromise;
      
      // Re-populate Authorization header and execute the replayed request
      if (originalRequest.headers) {
        originalRequest.headers[HEADER_NAMES.AUTHORIZATION] = `Bearer ${token}`;
      }

      return apiClient(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);
