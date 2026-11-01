import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { AnyFedSentinelEvent } from './types';
import { useAppStore } from '../store/appStore';

/**
 * WebSocketProvider establishes a connection to the backend event stream.
 * It automatically reconnects with exponential back‑off, fetches the latest
 * authoritative state on reconnect, and pushes events into the global store.
 */
export const WebSocketContext = createContext<WebSocket | null>(null);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const { applyEvent, fetchInitialState } = useAppStore();

  const connect = () => {
    // Assume the JWT token is stored in localStorage after login
    const token = localStorage.getItem('access_token');
    const apiBase = (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 'http://127.0.0.1:8000';
    const wsBase = apiBase.replace(/^http/, 'ws').replace(/\/+$/, '');
    const socket = new WebSocket(`${wsBase}/ws/events?token=${token || ''}`);

    socket.onopen = () => {
      console.log('WebSocket connected');
      reconnectAttempts.current = 0;
      // after connection, request the full state to guarantee sync
      fetchInitialState(token || '');
    };

    socket.onmessage = (event) => {
      try {
        const data: AnyFedSentinelEvent = JSON.parse(event.data);
        applyEvent(data);
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    socket.onclose = () => {
      console.warn('WebSocket closed, attempting reconnect');
      // exponential back‑off up to 30 seconds
      const timeout = Math.min(30000, 1000 * 2 ** reconnectAttempts.current);
      reconnectAttempts.current += 1;
      setTimeout(connect, timeout);
    };

    socket.onerror = (err) => {
      console.error('WebSocket error', err);
      socket.close();
    };

    setWs(socket);
  };

  useEffect(() => {
    connect();
    // cleanup on unmount
    return () => {
      ws?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <WebSocketContext.Provider value={ws}>{children}</WebSocketContext.Provider>;
};

export const useWebSocket = () => useContext(WebSocketContext);
