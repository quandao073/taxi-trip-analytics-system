import { useState, useEffect, useCallback } from 'react';
import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';

export const useRealtimeStats = () => {
  const [timelineData, setTimelineData] = useState(() => {
    const stored = localStorage.getItem("pickupTimeline");
    if (stored) {
      try {
        // Chuyển đổi timestamps từ chuỗi về đối tượng Date
        const parsed = JSON.parse(stored);
        return parsed.map(item => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
      } catch (e) {
        console.error("Error parsing stored timeline data:", e);
        return [];
      }
    }
    return [];
  });
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  const setupWebSocket = useCallback(() => {
    const socket = new SockJS('http://api-quanda.web-backend.local/ws');
    // const socket = new SockJS('http://localhost:8089/ws');
    const stompClient = new Client({
      webSocketFactory: () => socket,
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      onConnect: () => {
        setConnected(true);
        setError(null);
        stompClient.subscribe('/topic/realtime-trip', (message) => {
          try {
            const payload = JSON.parse(message.body);
            
            // Xử lý timestamp thành đối tượng Date
            const actualTimestamp = new Date(payload.timestamp);
            const predictedTimestamp = new Date(payload.predicted_timestamp);

            setTimelineData(prev => {
              // Cập nhật hoặc thêm mới dữ liệu thời gian thực
              let updated = [...prev];

              // Tìm và cập nhật/thêm mới bản ghi thời gian thực
              const actualIndex = updated.findIndex(
                item => item.timestamp.getTime() === actualTimestamp.getTime()
              );

              if (actualIndex !== -1) {
                // Cập nhật bản ghi hiện có
                updated[actualIndex] = {
                  ...updated[actualIndex],
                  tripCount: payload.trip_count,
                };
              } else {
                // Thêm bản ghi mới
                updated.push({
                  timestamp: actualTimestamp,
                  tripCount: payload.trip_count,
                  predictedTripCount: null
                });
              }

              // Tìm và cập nhật/thêm mới bản ghi dự đoán
              const predictedIndex = updated.findIndex(
                item => item.timestamp.getTime() === predictedTimestamp.getTime()
              );

              if (predictedIndex !== -1) {
                // Cập nhật bản ghi hiện có
                updated[predictedIndex] = {
                  ...updated[predictedIndex],
                  predictedTripCount: payload.predicted_trip_count
                };
              } else {
                // Thêm bản ghi mới
                updated.push({
                  timestamp: predictedTimestamp,
                  tripCount: null,
                  predictedTripCount: payload.predicted_trip_count
                });
              }

              // Sắp xếp dữ liệu theo thời gian
              return updated
                .sort((a, b) => a.timestamp - b.timestamp)
                // .slice(-240);
            });
          } catch (err) {
            console.error("JSON parse error:", err);
          }
        });
      },
      onDisconnect: () => setConnected(false),
      onStompError: (error) => setError(error.headers.message),
    });

    return stompClient;
  }, []);

  useEffect(() => {
    // Lưu dữ liệu vào localStorage
    try {
      const dataForStorage = timelineData.map(item => ({
        ...item,
        timestamp: item.timestamp instanceof Date ? item.timestamp.toISOString() : item.timestamp
      }));
      localStorage.setItem("pickupTimeline", JSON.stringify(dataForStorage));
    } catch (e) {
      console.error("Error saving timeline data to localStorage:", e);
    }
  }, [timelineData]);

  useEffect(() => {
    const client = setupWebSocket();
    client.activate();
    return () => {
      try {
        client.deactivate();
      } catch (e) {
        console.error("Error deactivating WebSocket client:", e);
      }
    };
  }, [setupWebSocket]);

  return { timelineData, connected, error };
};