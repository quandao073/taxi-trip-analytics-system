import { useState, useEffect, useCallback } from 'react';
import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';

export const usePickupStats = () => {
  const [data, setData] = useState([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  const setupWebSocket = useCallback(() => {
    // const socket = new SockJS('http://api-quanda.web-backend.local/ws');
    const socket = new SockJS('http://localhost:8089/ws');
    const stompClient = new Client({
      webSocketFactory: () => socket,
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      onConnect: () => {
        setConnected(true);
        setError(null);
        stompClient.subscribe('/topic/pickup-stats', (message) => {
          const newData = JSON.parse(message.body);
          setData(prev => {
            const existing = new Map(prev.map(item => [item.pickup_zone, item]));
            existing.set(newData.pickup_zone, newData);
            return Array.from(existing.values())
              .sort((a, b) => b.trip_count - a.trip_count)
              .slice(0, 10);
          });
        });
      },
      onDisconnect: () => setConnected(false),
      onStompError: (error) => setError(error.headers.message),
    });

    return stompClient;
  }, []);

  useEffect(() => {
    const client = setupWebSocket();
    client.activate();
    return () => client.deactivate();
  }, [setupWebSocket]);

  return { data, connected, error };
};
