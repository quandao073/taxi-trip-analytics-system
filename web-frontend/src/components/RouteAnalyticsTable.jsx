import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import availableZones from '../assets/zone';

const RouteAnalyticsTable = () => {
  const [selectedMonth, setSelectedMonth] = useState('2023-01');
  const [selectedZone, setSelectedZone] = useState('');
  const [searchZone, setSearchZone] = useState('');
  const [routeData, setRouteData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const debounceTimeout = useRef(null);

  const backendURI = 'http://localhost:8089';
  // const backendURI = 'http://api-quanda.web-backend.local'

  useEffect(() => {
    if (!selectedZone) return;

    const fetchRoutes = async () => {
      const [year, month] = selectedMonth.split('-').map(Number);
      setIsLoading(true);
      try {
        const res = await axios.get(`${backendURI}/analytics/routes/top`, {
          params: { year, month, zone: selectedZone }
        });
        const merged = [...(res.data.pickups || []), ...(res.data.dropoffs || [])];

        // Lọc trùng: loại bỏ những bản ghi pickupZone === dropoffZone === selectedZone
        const filtered = merged.filter(
          (item, index, self) =>
            !(item.pickupZone === selectedZone && item.dropoffZone === selectedZone) &&
            index === self.findIndex(i => (
              i.pickupZone === item.pickupZone &&
              i.dropoffZone === item.dropoffZone
            ))
        );

        setRouteData(filtered.slice(0, 10));
      } catch (err) {
        console.error('Error fetching route analytics:', err);
        setRouteData([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRoutes();
  }, [selectedMonth, selectedZone]);

  useEffect(() => {
    if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    debounceTimeout.current = setTimeout(() => {
      setSelectedZone(searchZone);
    }, 600);
    return () => clearTimeout(debounceTimeout.current);
  }, [searchZone]);

  return (
    <div>
      <h2 style={{ fontSize: '24px', margin: '20px 0', color: '#2c3e50', fontWeight: '700'}}>Thống kê tuyến đường phổ biến theo địa điểm</h2>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1 }}>
          <label style={{ fontWeight: '500' }}>Chọn tháng</label>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            style={{ 
              width: '100%',
              padding: '10px',
              border: '1px solid #cbd5e0',
              borderRadius: '6px',
              fontSize: '14px',
              transition: 'border-color 0.2s',
              marginTop: '10px'
            }}
          />
        </div>

        <div style={{ flex: 2 }}>
          <label style={{ fontWeight: '500' }}>Chọn địa điểm</label>
          <input
            list="zones"
            value={searchZone}
            onChange={(e) => setSearchZone(e.target.value)}
            placeholder="Nhập tên địa điểm..."
            style={{ 
              width: '100%',
              padding: '11.5px',
              border: '1px solid #cbd5e0',
              borderRadius: '6px',
              fontSize: '14px',
              transition: 'border-color 0.2s',
              marginTop: '10px'
            }}
          />
          <datalist id="zones">
            {availableZones.map((zone, idx) => (
              <option key={idx} value={zone} />
            ))}
          </datalist>
        </div>
      </div>

      {isLoading ? (
        <p>Đang tải dữ liệu...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead style={{ background: '#f7f7f7' }}>
            <tr>
              <th style={thStyle}>Điểm đón khách</th>
              <th style={thStyle}>Điểm trả khách</th>
              <th style={thStyle}>Số chuyến</th>
              <th style={thStyle}>Doanh thu</th>
              <th style={thStyle}>Khoảng cách TB (km)</th>
              <th style={thStyle}>Thời gian TB (phút)</th>
            </tr>
          </thead>
          <tbody>
            {routeData.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '16px' }}>Không có dữ liệu</td>
              </tr>
            ) : (
              routeData.map((item, idx) => (
                <tr key={idx}>
                  <td style={{
                    ...tdStyle,
                    fontWeight: item.pickupZone === selectedZone ? 'bold' : 'normal',
                    color: item.pickupZone === selectedZone ? '#2c7be5' : 'inherit'
                  }}>{item.pickupZone}</td>
                  <td style={{
                    ...tdStyle,
                    fontWeight: item.dropoffZone === selectedZone ? 'bold' : 'normal',
                    color: item.dropoffZone === selectedZone ? '#2c7be5' : 'inherit'
                  }}>{item.dropoffZone}</td>
                  <td style={tdStyle}>{item.tripCount}</td>
                  <td style={tdStyle}>{item.totalRevenue.toFixed(2)}$</td>
                  <td style={tdStyle}>{item.avgDistanceKm}</td>
                  <td style={tdStyle}>{item.avgDurationMinutes}</td>
                  <td style={tdStyle}>{item.avgSpeedKph}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

const thStyle = {
  padding: '12px',
  borderBottom: '1px solid #ddd',
  textAlign: 'left'
};

const tdStyle = {
  padding: '10px',
  borderBottom: '1px solid #eee'
};

export default RouteAnalyticsTable;
