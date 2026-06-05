import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth.store';
import DashboardLayout from '@/pages/DashboardLayout';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Onboarding from '@/pages/Onboarding';
import Dashboard from '@/pages/Dashboard';
import Ledger from '@/pages/Ledger';
import Simulator from '@/pages/Simulator';
import WageSync from '@/pages/WageSync';
import HealthMonitor from '@/pages/HealthMonitor';
import Developer from '@/pages/Developer';
import Billing from '@/pages/Billing';
import Founder from '@/pages/Founder';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/onboarding" element={<Onboarding />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="ledger" element={<Ledger />} />
        <Route path="simulator" element={<Simulator />} />
        <Route path="wage-sync" element={<WageSync />} />
        <Route path="health-monitor" element={<HealthMonitor />} />
        <Route path="developer" element={<Developer />} />
        <Route path="billing" element={<Billing />} />
        <Route path="founder" element={<Founder />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}