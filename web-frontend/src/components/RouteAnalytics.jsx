// import React, { useState } from 'react';
// import axios from 'axios';

// const RouteAnalytics = () => {
//   const [year, setYear] = useState('');
//   const [month, setMonth] = useState('');
//   const [zone, setZone] = useState('');
//   const [data, setData] = useState([]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     try {
//       const params = {};
//       if (year) params.year = year;
//       if (month) params.month = month;
//       if (zone) params.zone = zone;

//       const response = await axios.get('http://localhost:8089/analytics/routes', {
//         params,
//       });

//       setData(response.data);
//       console.log(response.data);
      
//     } catch (error) {
//       console.error('Failed to fetch route analytics:', error);
//     }
//   };

//   return (
//     <div style={{ padding: '1rem' }}>
//       <h2>Route Analytics by Zone</h2>

//       <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
//         <label>
//           Year:
//           <input type="number" value={year} onChange={(e) => setYear(e.target.value)} />
//         </label>
//         <label style={{ marginLeft: '1rem' }}>
//           Month:
//           <input type="number" value={month} onChange={(e) => setMonth(e.target.value)} />
//         </label>
//         <label style={{ marginLeft: '1rem' }}>
//           Zone:
//           <input type="text" value={zone} onChange={(e) => setZone(e.target.value)} />
//         </label>
//         <button type="submit" style={{ marginLeft: '1rem' }}>Fetch</button>
//       </form>

//       {data.length > 0 ? (
//         <table border="1" cellPadding="8">
//           <thead>
//             <tr>
//               <th>Year</th>
//               <th>Month</th>
//               <th>Pickup Zone</th>
//               <th>Dropoff Zone</th>
//               <th>Trip Count</th>
//               <th>Avg Distance (km)</th>
//               <th>Avg Duration (min)</th>
//               <th>Avg Fare</th>
//               <th>Total Revenue</th>
//             </tr>
//           </thead>
//           <tbody>
//             {data.map((row, index) => (
//               <tr key={index}>
//                 <td>{row.year}</td>
//                 <td>{row.month}</td>
//                 <td>{row.pickupZone}</td>
//                 <td>{row.dropoffZone}</td>
//                 <td>{row.tripCount}</td>
//                 <td>{row.avgDistanceKm}</td>
//                 <td>{row.avgDurationMinutes}</td>
//                 <td>{row.avgFare}</td>
//                 <td>{row.totalRevenue}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       ) : (
//         <p>No data found.</p>
//       )}
//     </div>
//   );
// };

// export default RouteAnalytics;
