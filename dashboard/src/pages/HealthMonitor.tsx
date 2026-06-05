import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '@/hooks/useLanguage';

export default function HealthMonitor() {
  const { t } = useTranslation();
  const { isRTL } = useLanguage();
  const [range, setRange] = useState('7');

  return (
    <div className="space-y-6 animate-slide-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('healthMonitor.title')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('healthMonitor.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Iqama Calendar */}
        <div className="content-card p-5">
          <h3 className="text-sm font-medium text-gray-500 mb-4">{t('healthMonitor.iqamaCalendar')}</h3>
          <div className="space-y-3">
            {[
              { label: t('healthMonitor.valid'), count: 1650, color: 'bg-status-ready' },
              { label: t('healthMonitor.expiringSoon'), count: 89, color: 'bg-status-review' },
              { label: t('healthMonitor.expired'), count: 23, color: 'bg-status-blocked' },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span className="text-sm text-gray-600">{item.label}</span>
                </div>
                <span className="text-sm font-semibold text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Contract Tracker */}
        <div className="content-card p-5">
          <h3 className="text-sm font-medium text-gray-500 mb-4">{t('healthMonitor.contractTracker')}</h3>
          <div className="space-y-3">
            {[
              { label: t('healthMonitor.activeContracts'), count: 1720, color: 'bg-status-ready' },
              { label: t('healthMonitor.expiringContracts'), count: 112, color: 'bg-status-review' },
              { label: t('healthMonitor.expiredContracts'), count: 10, color: 'bg-status-blocked' },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span className="text-sm text-gray-600">{item.label}</span>
                </div>
                <span className="text-sm font-semibold text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Compliance Trends */}
      <div className="content-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-500">{t('healthMonitor.complianceTrends')}</h3>
          <div className="flex gap-1">
            {[
              { key: '7', label: t('healthMonitor.last7Days') },
              { key: '30', label: t('healthMonitor.last30Days') },
              { key: '90', label: t('healthMonitor.last90Days') },
            ].map((r) => (
              <button
                key={r.key}
                onClick={() => setRange(r.key)}
                className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors ${
                  range === r.key
                    ? 'bg-primary/10 text-primary'
                    : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Trend bars */}
        <div className="h-48 flex items-end justify-between gap-2 pt-4">
          {[75, 72, 78, 76, 80, 79, 82, 81, 83, 85, 84, 87, 86, 88].map((val, i) => (
            <div
              key={i}
              className="flex-1 rounded-t-md transition-all duration-300 hover:opacity-80 relative group"
              style={{
                height: `${val * 2}px`,
                backgroundColor: val >= 80 ? '#3ECF8E' : val >= 60 ? '#F5A623' : '#E53E3E',
                minWidth: '8px',
              }}
            >
              <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                {val}%
              </span>
            </div>
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-2">
          <span>Apr 1</span>
          <span>Apr 7</span>
          <span>Apr 14</span>
          <span>Apr 21</span>
          <span>Apr 28</span>
        </div>
      </div>
    </div>
  );
}