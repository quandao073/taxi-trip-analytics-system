import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Service from './pages/Service';


const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/dashboard', element: <Dashboard /> },
  { path: '/service', element: <Service />}
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
