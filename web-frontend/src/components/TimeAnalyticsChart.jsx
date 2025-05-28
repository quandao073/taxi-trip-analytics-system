import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const TimeAnalyticsChart = () => {
  const [startMonth, setStartMonth] = useState('2023-01');
  const [endMonth, setEndMonth] = useState('2023-12');
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const backendURI = 'http://localhost:8089'
  // const backendURI = 'http://api-quanda.web-backend.local'

  // Tự động fetch data khi thay đổi khoảng thời gian
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [startYear, startMonthNum] = startMonth.split('-').map(Number);
        const [endYear, endMonthNum] = endMonth.split('-').map(Number);

        const res = await axios.get(`${backendURI}/analytics/time/range`, {
          params: { startYear, startMonth: startMonthNum, endYear, endMonth: endMonthNum }
        });

        const transformed = res.data.map(item => ({
          ...item,
          monthYear: `${item.month.toString().padStart(2, '0')}/${item.year}`,
          revenueInMillions: (item.totalRevenue / 10).toFixed(1),
          tripCountInThousands: (item.tripCount).toFixed(0)
        }));

        setChartData(transformed);
      } catch (err) {
        console.error('Fetch data error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [startMonth, endMonth]);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload.length) return null;

    const data = payload[0].payload;
    return (
      <div className="custom-tooltip" style={{
        background: '#fff',
        padding: '12px',
        border: '1px solid #ddd',
        borderRadius: '4px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h4 style={{ marginBottom: '8px', color: '#333' }}>Tháng {data.monthYear}</h4>
        <div style={{ display: 'grid', gap: '4px' }}>
          <div style={{ color: '#8884d8' }}>
            Doanh thu: <strong>{(data.totalRevenue)}$</strong>
          </div>
          <div style={{ color: '#82ca9d' }}>
            Số chuyến: <strong>{(data.tripCount)}</strong>
          </div>
          <div style={{ color: '#ff7300' }}>
            Quãng đường TB: <strong>{data.avgDistanceKm} km</strong>
          </div>
          <div style={{ color: '#387908' }}>
            Thời gian TB: <strong>{data.avgDurationMinutes} phút</strong>
          </div>
          <div style={{ color: '#a0522d' }}>
            Tốc độ TB: <strong>{data.avgSpeedKph} km/h</strong>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{margin: '0 auto' }}>
      <h2 style={{ fontSize: '24px', marginBottom: '24px', color: '#2c3e50', fontWeight: '700' }}>
        Thống kê dữ liệu theo tháng
      </h2>

      {/* Date Picker Container */}
      <div style={{
        display: 'flex',
        gap: '16px',
        marginBottom: '32px',
        flexWrap: 'wrap',
        alignItems: 'flex-end'
      }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '500',
            color: '#4a5568'
          }}>
            Từ tháng
          </label>
          <input
            type="month"
            value={startMonth}
            onChange={(e) => setStartMonth(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #cbd5e0',
              borderRadius: '6px',
              fontSize: '14px',
              transition: 'border-color 0.2s',
              ':focus': {
                outline: 'none',
                borderColor: '#4299e1',
                boxShadow: '0 0 0 1px #4299e1'
              }
            }}
          />
        </div>

        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '500',
            color: '#4a5568'
          }}>
            Đến tháng
          </label>
          <input
            type="month"
            value={endMonth}
            onChange={(e) => setEndMonth(e.target.value)}
            min={startMonth}
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #cbd5e0',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>
      </div>

      {isLoading ? (
        <div style={{
          height: '400px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#718096'
        }}>
          Đang tải dữ liệu...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={600} >
          <ComposedChart
            data={chartData}
            margin={{ top: 50, right: 82, left: 82, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="monthYear"
              angle={-45}
              textAnchor="end"
              tick={{ fontSize: 12, fill: '#4a5568' }}
              height={70}
            />
            <YAxis
              yAxisId="left"
              label={{
                value: 'Doanh thu (x0.1) / Số chuyến',
                angle: 0,
                position: 'top',
                offset: 20
              }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              label={{
                value: 'Thông số TB (km / phút / km/h)',
                angle: 0,
                position: 'top',
                offset: 20
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                paddingTop: '20px',
                display: 'flex',
                justifyContent: 'center',
                gap: '20px'
              }}
            />

            {/* Bars */}
            <Bar
              yAxisId="left"
              dataKey="revenueInMillions"
              name="Doanh thu"
              fill="#8884d8"
              radius={[4, 4, 0, 0]}
              barSize={30}
            />
            <Bar
              yAxisId="left"
              dataKey="tripCountInThousands"
              name="Số chuyến"
              fill="#82ca9d"
              radius={[4, 4, 0, 0]}
              barSize={30}
            />

            {/* Lines */}
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="avgDistanceKm"
              name="Quãng đường TB"
              stroke="#ff7300"
              strokeWidth={2}
              dot={{ r: 4, fill: '#ff7300' }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="avgDurationMinutes"
              name="Thời gian TB"
              stroke="#387908"
              strokeWidth={2}
              dot={{ r: 4, fill: '#387908' }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="avgSpeedKph"
              name="Tốc độ TB"
              stroke="#a0522d"
              strokeWidth={2}
              dot={{ r: 4, fill: '#a0522d' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default TimeAnalyticsChart;