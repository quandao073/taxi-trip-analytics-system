import { useEffect, useState } from 'react';
import '../css/Clock.css'

// export default function Clock({ initialTime }) {
//   const [time, setTime] = useState(new Date(initialTime));

//   useEffect(() => {
//     const timer = setInterval(() => {
//       setTime(prev => new Date(prev.getTime() + 1000));
//     }, 1000);

//     return () => clearInterval(timer);
//   }, []);

//   const format = (date) =>
//     date.toLocaleString('vi-VN', { hour12: false });

//   return (
//     <div className="dashboard-clock">
//       <span>{format(time)}</span>
//     </div>
//   );
// }


export default function Clock({ initialTime = "2024-01-01T00:00:00" }) {
    const STORAGE_KEY = 'simulated-start-real-time';

    const [realStartTime] = useState(() => {
        const saved = localStorage.getItem(STORAGE_KEY);
        const now = Date.now();

        if (saved) {
            return parseInt(saved);
        } else {
            localStorage.setItem(STORAGE_KEY, now.toString());
            return now;
        }
    });

    const baseTime = new Date(initialTime);
    const [simTime, setSimTime] = useState(() => new Date(baseTime.getTime() + (Date.now() - realStartTime)));

    useEffect(() => {
        const interval = setInterval(() => {
            const now = Date.now();
            setSimTime(new Date(baseTime.getTime() + (now - realStartTime)));
        }, 1000);

        return () => clearInterval(interval);
    }, [baseTime, realStartTime]);

    const format = (date) =>
        date.toLocaleString('vi-VN', { hour12: false });


    return (
        <div className="dashboard-clock">
            <span>{format(simTime)}</span>
            <button className='reset-time-btn' onClick={() => {
                localStorage.removeItem('simulated-start-real-time');
                window.location.reload();
            }}>Reset</button>
        </div>
    );
}