import React, { useEffect, useState, useCallback } from 'react';
import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';

function App() {
  const [data, setData] = useState([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  // Khởi tạo WebSocket client
  const setupWebSocket = useCallback(() => {
    const socket = new SockJS('http://localhost:8089/ws');
    const stompClient = new Client({
      webSocketFactory: () => socket,
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      onConnect: () => {
        console.log("✅ Connected to WebSocket");
        setConnected(true);
        setError(null);
        
        // Subscribe topic nhận dữ liệu pickup stats
        stompClient.subscribe('/topic/pickup-stats', (message) => {
          const newData = JSON.parse(message.body);
          console.log("📊 New data received:", newData);
          
          setData(prev => {
            const existing = new Map(prev.map(item => [item.pickup_zone, item]));
            existing.set(newData.pickup_zone, newData);
          
            return Array.from(existing.values())
              .sort((a, b) => b.trip_count - a.trip_count)
              .slice(0, 10);
          });
          
        });
      },
      onDisconnect: () => {
        console.log("⚠️ Disconnected from WebSocket");
        setConnected(false);
      },
      onStompError: (error) => {
        console.error("❌ WebSocket error:", error);
        setError(error.headers.message);
      }
    });

    return stompClient;
  }, []);

  useEffect(() => {
    const stompClient = setupWebSocket();
    stompClient.activate();

    return () => {
      stompClient.deactivate();
      console.log("🧹 Cleanup WebSocket connection");
    };
  }, [setupWebSocket]);

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ marginBottom: 20 }}>
        <h2>🚕 Top 10 Pickup Zones (Real-time)</h2>
        <div style={{ color: connected ? 'green' : 'red' }}>
          {connected ? '🟢 Đang kết nối real-time' : '🔴 Mất kết nối'}
        </div>
        {error && <div style={{ color: 'red' }}>Lỗi: {error}</div>}
      </div>

      {/* Bảng dữ liệu */}
      <table border="1" cellPadding="10" style={{ 
        marginTop: "20px", 
        width: "100%", 
        borderCollapse: "collapse",
        opacity: connected ? 1 : 0.5 
      }}>
        <thead>
          <tr>
            <th>Zone</th>
            <th>Trip Count</th>
            <th>Total Revenue ($)</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              <td>{row.pickup_zone}</td>
              <td>{row.trip_count}</td>
              <td>{row.total_revenue?.toFixed(2) || '0.00'}</td>
            </tr>
          ))}
          {data.length === 0 && (
            <tr>
              <td colSpan="3" style={{ textAlign: 'center' }}>
                {connected ? 'Đang nhận dữ liệu...' : 'Kết nối lại để nhận dữ liệu'}
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Biểu đồ */}
      <div style={{ height: 500, marginTop: 50 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="pickup_zone" 
              interval={0} 
              angle={-30} 
              textAnchor="end" 
              height={100}
              tick={{ fontSize: 12 }}
            />
            <YAxis />
            <Tooltip 
              formatter={(value) => [value.toFixed(2), 'USD']}
              contentStyle={{ 
                backgroundColor: '#333',
                border: 'none',
                borderRadius: 5,
                color: '#fff'
              }}
            />
            <Bar 
              dataKey="total_revenue" 
              fill="#82ca9d" 
              name="Total Revenue"
              animationDuration={300}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default App;