// import '../css/Dashboard.css'
// export default function RealTimeTable({ data, connected }) {
//   return (
//     <table className={`realtime-table ${connected ? 'realtime-table--connected' : 'realtime-table--disconnected'}`}>
//       <thead>
//         <tr>
//           <th>Khu vực</th>
//           <th>Số chuyến đi</th>
//           {/* <th>Total Revenue ($)</th> */}
//         </tr>
//       </thead>
//       <tbody>
//         {data.map((row, idx) => (
//           <tr key={idx}>
//             <td>{row.pickup_zone}</td>
//             <td>{row.trip_count}</td>
//             {/* <td>{row.total_revenue?.toFixed(2) || '0.00'}</td> */}
//           </tr>
//         ))}
//         {data.length === 0 && (
//           <tr>
//             <td colSpan="2" className="realtime-table__empty">
//               {connected ? 'Đang nhận dữ liệu...' : 'Kết nối lại để nhận dữ liệu'}
//             </td>
//           </tr>
//         )}
//       </tbody>
//     </table>
//   );
// }
