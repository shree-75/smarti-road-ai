/**
 * @fileoverview telemetryService.js - Telemetry API Service Module
 * @module services/telemetryService
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Wrap telemetry REST endpoint queries.
 * - Perform error mapping and normalization.
 * 
 * Exported APIs:
 * - getLatestTelemetry()
 * - getTelemetryHistory()
 * - postTelemetry()
 * 
 * Dependencies:
 * - api/axios
 */

import { apiClient } from '../api/axios.js';

/**
 * Endpoint for telemetry REST operations.
 */
const TELEMETRY_PATH = '/telemetry';

/**
 * Fetches the single most recent telemetry record for the authenticated user session.
 * 
 * @async
 * @returns {Promise<{ success: boolean, data?: object, error?: object }>}
 */
export const getLatestTelemetry = async () => {
  try {
    const response = await apiClient.get(`${TELEMETRY_PATH}/latest`);
    return { success: true, data: response.data };
  } catch (error) {
    const status = error.response?.status;
    const message = error.response?.data?.detail || 'Failed to fetch telemetry data.';
    return {
      success: false,
      status,
      error: { message, status }
    };
  }
};

/**
 * Fetches the historical list of telemetry entries for the authenticated user session.
 * 
 * @async
 * @param {number} [limit=50] - Number of records to return.
 * @returns {Promise<{ success: boolean, data?: Array, error?: object }>}
 */
export const getTelemetryHistory = async (limit = 50) => {
  try {
    const response = await apiClient.get(TELEMETRY_PATH, { params: { limit } });
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: { message: error.response?.data?.detail || 'Failed to fetch telemetry history.' }
    };
  }
};

/**
 * Transmits a new telemetry payload to the server.
 * 
 * @async
 * @param {object} telemetryData - Sensor reading object.
 * @returns {Promise<{ success: boolean, data?: object, error?: object }>}
 */
export const postTelemetry = async (telemetryData) => {
  try {
    const response = await apiClient.post(TELEMETRY_PATH, telemetryData);
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: { message: error.response?.data?.detail || 'Failed to post telemetry reading.' }
    };
  }
};

export default {
  getLatestTelemetry,
  getTelemetryHistory,
  postTelemetry
};
