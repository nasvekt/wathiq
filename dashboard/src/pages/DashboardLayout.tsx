import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Sidebar from '@/components/layout/Sidebar';
import TopBar from '@/components/layout/TopBar';

// Map routes to titles
const routeTitles: Record<string, string> = {
  '/': 'dashboard.title',
  '/ledger': 'ledger.title',
  '/simulator': 'simulator.title',
  '/wage-sync': 'wageSync.title',
  '/health-monitor': 'healthMonitor.title',
  '/developer': 'developer.title',
  '/billing': 'billing.title',
  '/founder': 'founder.title',
};

export default function DashboardLayout() {
  const { t } = useTranslation();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const titleKey = routeTitles[location.pathname];
  const title = titleKey ? t(titleKey) : '';

  return (
    <div className="flex h-screen bg-surface-content">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
          title={title}
        />

        <main className="flex-1 overflow-y-auto px-4 lg:px-6 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}