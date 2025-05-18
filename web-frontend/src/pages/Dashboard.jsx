import { usePickupStats } from '../hooks/usePickupStats';
// import StatusIndicator from '../components/StatusIndicator';
// import RealTimeTable from '../components/RealTimeTable';
import RealTimeChart from '../components/RealTimeChart';
import '../css/Dashboard.css'

export default function Dashboard() {
  const { timelineData, connected, error } = usePickupStats();
  console.log("Dashboard data: ", timelineData);
  
  return (
    <div className='dashboard-wrapper'>
      {/* <h2 className='dashboard-realtime-header'>Dữ liệu thời gian thực</h2> */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h2 className='dashboard-realtime-header'>Dữ liệu thời gian thực</h2>
        
      </div>

      <div className='dashboard-realtime-container'>
        {/* <div className='realtime-table-container'>
          <h3>Top 10 khu vực có số chuyến đi nhiều nhất</h3>
          <RealTimeTable data={data} connected={connected} />
        </div> */}
        <div className='realtime-chart-container'>
          <h3>Biểu đồ số chuyến đi theo thời gian thực</h3>
          <RealTimeChart data={timelineData} />
        </div>
      </div>
      {/* <StatusIndicator connected={connected} error={error} /> */}
    </div>
  );
}
