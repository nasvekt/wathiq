import { useTranslation } from 'react-i18next';
import { useDashboard } from '@/hooks/useCompliance';
import { useLanguage } from '@/hooks/useLanguage';
import ComplianceScoreRing from '@/components/dashboard/ComplianceScoreRing';
import NitaqatBandCard from '@/components/dashboard/NitaqatBandCard';
import PenaltyExposureCard from '@/components/dashboard/PenaltyExposureCard';
import type { NitaqatBand } from '@/types/employee';

export default function Dashboard() {
  const { t } = useTranslation();
  const { isRTL } = useLanguage();
  const { data, isLoading, error } = useDashboard();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-gray-400">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-status-blocked text-sm mb-2">{t('common.error')}</p>
          <button
            onClick={() => window.location.reload()}
            className="text-primary text-sm hover:underline"
          >
            {t('common.retry')}
          </button>
        </div>
      </div>
    );
  }

  const dashboard = data ?? {
    health_score: 78,
    previous_health_score: 72,
    nitaqat_band: 'high_green' as NitaqatBand,
    nitaqat_percentage: 14.5,
    total_records: 1842,
    ready_count: 1423,
    review_count: 267,
    blocked_count: 89,
    at_risk_count: 63,
    penalty_exposure: 187500,
    saudi_count: 245,
    expat_count: 1597,
  };

  return (
    <div className="space-y-6 animate-slide-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('dashboard.subtitle')}</p>
      </div>

      {/* Top row — Score ring + Nitaqat band + Penalty */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ComplianceScoreRing
          score={dashboard.health_score}
          previousScore={dashboard.previous_health_score ?? 72}
        />
        <NitaqatBandCard
          band={dashboard.nitaqat_band as NitaqatBand}
          percentage={dashboard.nitaqat_percentage}
          saudiCount={dashboard.saudi_count}
          expatCount={dashboard.expat_count}
        />
        <PenaltyExposureCard
          amount={dashboard.penalty_exposure}
          blockedCount={dashboard.blocked_count}
          atRiskCount={dashboard.at_risk_count}
        />
      </div>

      {/* Status breakdown */}
      <div className="content-card p-5">
        <h3 className="text-sm font-medium text-gray-500 mb-4">{t('dashboard.totalRecords')}</h3>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          {([
            { label: t('dashboard.ready'), count: dashboard.ready_count, color: 'bg-status-ready' },
            { label: t('dashboard.review'), count: dashboard.review_count, color: 'bg-status-review' },
            { label: t('dashboard.blocked'), count: dashboard.blocked_count, color: 'bg-status-blocked' },
            { label: t('dashboard.atRisk'), count: dashboard.at_risk_count, color: 'bg-status-at-risk' },
            { label: t('dashboard.pending'), count: dashboard.pending_count ?? 0, color: 'bg-status-pending' },
          ] as const).map((item) => (
            <div key={item.label} className="p-4 bg-gray-50 rounded-lg text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                <span className="text-xs text-gray-500">{item.label}</span>
              </div>
              <span className="text-2xl font-bold text-gray-900">{item.count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent activity placeholder */}
      <div className="content-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-500">{t('dashboard.recentActivity')}</h3>
          <button className="text-xs text-primary hover:text-primary-dark font-medium">
            {t('common.viewAll')}
          </button>
        </div>
        <div className="space-y-3">
          {[
            { type: 'success', message: 'Batch #1243 processed — 1,842 records updated', time: '2 min ago' },
            { type: 'warning', message: '12 iqamas expiring within 30 days', time: '15 min ago' },
            { type: 'info', message: 'Nitaqat band recalculated: High Green (14.5%)', time: '1 hour ago' },
            { type: 'error', message: 'SIF export failed for batch #1240 — missing bank codes', time: '3 hours ago' },
          ].map((activity, i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                activity.type === 'success' ? 'bg-status-ready' :
                activity.type === 'warning' ? 'bg-status-review' :
                activity.type === 'error' ? 'bg-status-blocked' :
                'bg-status-pending'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700">{activity.message}</p>
                <p className="text-xs text-gray-400 mt-0.5">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}