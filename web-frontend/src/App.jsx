import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';

function App() {
  const [data, setData] = useState([]);

  const fetchData = () => {
    axios.get('http://localhost:8089/api/realtime/zone/top')
      .then(res => {
        console.log("✅ Dữ liệu cập nhật:", res.data);
        setData(res.data);
      })
      .catch(err => {
        console.error("❌ Failed to fetch data:", err);
      });
  };

  useEffect(() => {
    fetchData(); // gọi lần đầu
    const interval = setInterval(fetchData, 10000); // gọi lại mỗi 10 giây

    return () => clearInterval(interval); // cleanup khi component unmount
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h2>🚕 Top 10 Pickup Zones (Real-time)</h2>

      {/* Bảng dữ liệu */}
      <table border="1" cellPadding="10" style={{ marginTop: "20px", width: "100%", borderCollapse: "collapse" }}>
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
              <td>{row.zone}</td>
              <td>{row.trip_count}</td>
              <td>{row.total_revenue.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Biểu đồ */}
      <div style={{ height: 500, marginTop: 50 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="zone" interval={0} angle={-30} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total_revenue" fill="#82ca9d" name="Total Revenue ($)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default App;
