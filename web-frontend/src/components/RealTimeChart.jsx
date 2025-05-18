import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { format, addHours, subHours, addMinutes, isAfter, isBefore } from 'date-fns';

export default function RealTimeChart({ data }) {
  // Xác định thời điểm hiện tại (bản ghi thời gian thực mới nhất)
  const currentTime = useMemo(() => {
    if (!data || data.length === 0) return new Date();
    
    // Tìm bản ghi thời gian thực mới nhất
    const actualData = data.filter(d => d.tripCount !== null);
    if (actualData.length === 0) return new Date();
    
    return actualData.reduce((latest, item) => {
      const itemTime = item.timestamp instanceof Date 
        ? item.timestamp 
        : new Date(item.timestamp);
      return isAfter(itemTime, latest) ? itemTime : latest;
    }, new Date(0));
  }, [data]);

  // Tạo khoảng thời gian ±1 giờ từ thời điểm hiện tại
  const timeWindow = useMemo(() => {
    const startTime = subHours(currentTime, 1);
    const endTime = addHours(currentTime, 1);
    return { startTime, endTime };
  }, [currentTime]);

  // Tạo mảng các tick mốc thời gian mỗi 5 phút
  const timeTicks = useMemo(() => {
    const { startTime, endTime } = timeWindow;
    const ticks = [];
    let current = new Date(startTime);
    
    while (isBefore(current, endTime)) {
      ticks.push(new Date(current));
      current = addMinutes(current, 5); // Mỗi 5 phút một tick
    }
    
    return ticks;
  }, [timeWindow]);

  // Tạo dữ liệu hiển thị liên tục thời gian thực và dự đoán
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Chuyển đổi dữ liệu để đảm bảo timestamp là Date object
    const normalizedData = data.map(item => ({
      ...item,
      timestamp: item.timestamp instanceof Date ? item.timestamp : new Date(item.timestamp)
    }));
    
    // Lọc dữ liệu trong khoảng thời gian hiển thị
    const { startTime, endTime } = timeWindow;
    const filteredData = normalizedData.filter(item => 
      !isBefore(item.timestamp, startTime) && !isAfter(item.timestamp, endTime)
    );
    
    // Tạo một Map để lưu dữ liệu theo timestamp
    const dataMap = new Map();
    
    // Xử lý dữ liệu thời gian thực
    filteredData
      .filter(item => item.tripCount !== null)
      .forEach(item => {
        const timeKey = item.timestamp.getTime();
        if (!dataMap.has(timeKey)) {
          dataMap.set(timeKey, { timestamp: item.timestamp, tripCount: item.tripCount });
        } else {
          dataMap.get(timeKey).tripCount = item.tripCount;
        }
      });
    
    // Xử lý dữ liệu dự đoán
    filteredData
      .filter(item => item.predictedTripCount !== null)
      .forEach(item => {
        const timeKey = item.timestamp.getTime();
        if (!dataMap.has(timeKey)) {
          dataMap.set(timeKey, { timestamp: item.timestamp, predictedTripCount: item.predictedTripCount });
        } else {
          dataMap.get(timeKey).predictedTripCount = item.predictedTripCount;
        }
      });
    
    // Chuyển đổi Map thành mảng và sắp xếp theo thời gian
    return Array.from(dataMap.values()).sort((a, b) => a.timestamp - b.timestamp);
  }, [data, timeWindow]);

  // Tạo đường dự đoán kết nối với đường thời gian thực
  const combinedSeries = useMemo(() => {
    if (chartData.length === 0) return [];
    
    // Tìm giá trị tripCount cuối cùng (thời điểm hiện tại)
    const lastActualPoint = [...chartData]
      .filter(d => d.tripCount !== null)
      .sort((a, b) => b.timestamp - a.timestamp)[0];
    
    if (!lastActualPoint) return chartData;
    
    // Tạo một điểm kết nối giữa thời gian thực và dự đoán
    const connectingPoint = {
      timestamp: lastActualPoint.timestamp,
      tripCount: null,
      predictedTripCount: lastActualPoint.tripCount // Điểm kết nối lấy giá trị từ điểm cuối thời gian thực
    };
    
    // Chèn điểm kết nối vào dữ liệu
    const result = [...chartData];
    const connectingPointIndex = result.findIndex(d => 
      d.timestamp.getTime() === lastActualPoint.timestamp.getTime()
    );
    
    if (connectingPointIndex !== -1) {
      // Cập nhật điểm hiện có nếu đã tồn tại
      result[connectingPointIndex].predictedTripCount = lastActualPoint.tripCount;
    }
    
    return result;
  }, [chartData]);

  // Custom tooltip hiển thị thời gian và số liệu
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const time = format(new Date(label), 'HH:mm:ss');
      const isPrediction = new Date(label) > currentTime;
      
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.9)', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '5px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p className="label" style={{ fontWeight: 'bold', marginBottom: '5px' }}>
            {`Thời gian: ${time}`}
          </p>
          <p style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>
            {isPrediction ? '(Dự đoán)' : '(Thực tế)'}
          </p>
          {payload.map((entry, index) => (
            entry.value !== null && (
              <p key={`item-${index}`} style={{ 
                color: entry.color,
                fontWeight: 'bold',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>{`${entry.name}:`}</span>
                <span style={{ marginLeft: '10px' }}>{entry.value}</span>
              </p>
            )
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={combinedSeries} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="timestamp" 
          type="number"
          domain={[timeWindow.startTime.getTime(), timeWindow.endTime.getTime()]}
          scale="time"
          ticks={timeTicks.map(d => d.getTime())}
          tickFormatter={(unixTime) => format(new Date(unixTime), 'HH:mm')}
          minTickGap={50}
        />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        
        {/* Đường thời gian thực - chỉ hiển thị từ đầu đến thời điểm hiện tại */}
        <Line
          name="Số chuyến đi thực tế"
          type="monotone"
          dataKey="tripCount"
          stroke="#007bff"
          strokeWidth={3}
          dot={false}
          connectNulls={true}
          isAnimationActive={false}
        />
        
        {/* Đường dự đoán - hiển thị từ thời điểm hiện tại đến cuối */}
        <Line
          name="Dự đoán"
          type="monotone"
          dataKey="predictedTripCount"
          stroke="#f39c12"
          strokeDasharray="5 5"
          strokeWidth={2}
          dot={false}
          connectNulls={true}
          isAnimationActive={false}
        />
        
        {/* Đường phân cách thời gian thực và dự đoán */}
        <ReferenceLine 
          x={currentTime.getTime()} 
          stroke="rgba(255, 0, 0, 0.5)" 
          strokeWidth={1}
          label={{ 
            value: 'Hiện tại', 
            position: 'insideTopRight', 
            fill: 'red',
            fontSize: 12
          }} 
        />
      </LineChart>
    </ResponsiveContainer>
  );
}