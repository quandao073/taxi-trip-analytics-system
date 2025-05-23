import { useRealtimeStats } from '../hooks/useRealtimeStats';
import RealTimeChart from '../components/RealTimeChart';
import '../css/Dashboard.css';
import { format } from 'date-fns';
import TimeAnalyticsChart from '../components/TimeAnalyticsChart';

export default function Dashboard() {
  const { timelineData, connected, error } = useRealtimeStats();
  console.log("Dashboard data: ", timelineData);

  const latestTime = timelineData.length > 0
    ? new Date(timelineData[timelineData.length - 1].timestamp)
    : null;

  const formattedDate = latestTime
    ? format(latestTime, 'dd/MM/yyyy')
    : '---';

  return (
    <div className='dashboard-wrapper'>
      <div style={{ display: 'flex', justifyContent: 'space-between'}}>
        <h2 className='dashboard-realtime-header'>Dữ liệu thời gian thực</h2>
      </div>

      <div className='dashboard-realtime-container'>
        <div className='realtime-chart-container'>
          <h3 style={{marginBottom:'20px' }}>Biểu đồ số chuyến đi theo thời gian thực ngày ({formattedDate})</h3>
          <RealTimeChart data={timelineData} />
        </div>
      </div>

      <TimeAnalyticsChart />

    </div>
  );
}
