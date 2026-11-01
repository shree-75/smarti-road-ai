/**
 * @fileoverview websocketService.js - Telemetry Real-Time WebSocket Service Client
 * @module services/websocketService
 * @version 1.0.0
 * @author Antigravity Pair Programmer
 * 
 * Responsibilities:
 * - Manage WebSocket connections to the FastAPI backend.
 * - Authenticate via in-memory JWT token.
 * - Reconnect automatically with backoff delay.
 * - Broadcast received telemetry payloads to subscriber callbacks.
 * 
 * Exported APIs:
 * - connectTelemetryWebSocket()
 * 
 * Dependencies:
 * - utils/token
 */

import { getAccessToken } from '../utils/token.js';
import { DEFAULT_API_URL } from '../constants/api.constants.js';

/**
 * Resolves the WebSocket URL dynamically from API base URL.
 * Converts http:// or https:// to ws:// or wss://.
 * 
 * @returns {string} The WebSocket endpoint URL.
 */
const resolveWsUrl = () => {
  let baseUrl = DEFAULT_API_URL;
  try {
    baseUrl = import.meta.env.VITE_API_URL || DEFAULT_API_URL;
  } catch (_e) {
    baseUrl = DEFAULT_API_URL;
  }

  const wsScheme = baseUrl.startsWith('https') ? 'wss' : 'ws';
  const cleanHostPath = baseUrl.replace(/^https?:\/\//, '');
  return `${wsScheme}://${cleanHostPath}/telemetry/ws`;
};

/**
 * Connects to the telemetry WebSocket endpoint with automatic reconnection.
 * 
 * @param {object} options
 * @param {function(object): void} options.onMessage - Called when a new telemetry payload arrives.
 * @param {function(string): void} options.onStatusChange - Called with connection status ('connecting', 'connected', 'disconnected', 'reconnecting').
 * @returns {function(): void} Unsubscribe/disconnect handler function.
 */
export const connectTelemetryWebSocket = ({ onMessage, onStatusChange }) => {
  let socket = null;
  let reconnectTimer = null;
  let isIntentionallyClosed = false;
  let reconnectAttempts = 0;
  const maxReconnectDelay = 10000;

  const notifyStatus = (status) => {
    if (onStatusChange && typeof onStatusChange === 'function') {
      onStatusChange(status);
    }
  };

  const connect = () => {
    const token = getAccessToken();
    if (!token) {
      notifyStatus('disconnected');
      return;
    }

    notifyStatus(reconnectAttempts > 0 ? 'reconnecting' : 'connecting');

    const wsUrl = `${resolveWsUrl()}?token=${encodeURIComponent(token)}`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      reconnectAttempts = 0;
      notifyStatus('connected');
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload && payload.type === 'telemetry' && payload.data) {
          if (onMessage && typeof onMessage === 'function') {
            onMessage(payload.data);
          }
        }
      } catch (err) {
        console.warn('Failed to parse WebSocket telemetry message:', err);
      }
    };

    socket.onerror = (error) => {
      console.warn('Telemetry WebSocket error:', error);
    };

    socket.onclose = (event) => {
      if (isIntentionallyClosed) {
        notifyStatus('disconnected');
        return;
      }

      notifyStatus('reconnecting');
      reconnectAttempts += 1;
      const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), maxReconnectDelay);
      
      reconnectTimer = setTimeout(() => {
        if (!isIntentionallyClosed) {
          connect();
        }
      }, delay);
    };
  };

  connect();

  // Return teardown / disconnect cleanup function
  return () => {
    isIntentionallyClosed = true;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
    }
    if (socket) {
      socket.close();
    }
    notifyStatus('disconnected');
  };
};

export default connectTelemetryWebSocket;
