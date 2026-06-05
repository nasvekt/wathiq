import { useTranslation } from 'react-i18next';

interface PenaltyExposureCardProps {
  amount: number;
  blockedCount?: number;
  atRiskCount?: number;
}

export default function PenaltyExposureCard({
  amount,
  blockedCount = 0,
  atRiskCount = 0,
}: PenaltyExposureCardProps) {
  const { t } = useTranslation();

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-SA', {
      style: 'currency',
      currency: 'SAR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const severity = amount >= 100000 ? 'high' : amount >= 50000 ? 'medium' : 'low';

  const severityConfig = {
    high: { color: '#E53E3E', bg: 'rgba(229, 62, 62, 0.08)', label: 'High Risk' },
    medium: { color: '#F97316', bg: 'rgba(249, 115, 22, 0.08)', label: 'Moderate Risk' },
    low: { color: '#3ECF8E', bg: 'rgba(62, 207, 142, 0.08)', label: 'Low Risk' },
  };

  const config = severityConfig[severity];

  return (
    <div className="content-card p-5">
      <h3 className="text-sm font-medium text-gray-500 mb-4">{t('dashboard.penaltyExposure')}</h3>

      {/* Amount */}
      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-3xl font-bold text-gray-900">
          {formatCurrency(amount)}
        </span>
        <span className="text-xs text-gray-400">SAR</span>
      </div>

      <p className="text-xs text-gray-400 mb-4">{t('dashboard.estimatedMonthly')}</p>

      {/* Severity badge */}
      <div
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium mb-4"
        style={{
          backgroundColor: config.bg,
          color: config.color,
        }}
      >
        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: config.color }} />
        {config.label}
      </div>

      {/* Breakdown */}
      <div className="space-y-2 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-status-blocked" />
            <span className="text-sm text-gray-600">{t('dashboard.blocked')}</span>
          </div>
          <span className="text-sm font-semibold text-gray-900">{blockedCount}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-status-at-risk" />
            <span className="text-sm text-gray-600">{t('dashboard.atRisk')}</span>
          </div>
          <span className="text-sm font-semibold text-gray-900">{atRiskCount}</span>
        </div>
      </div>
    </div>
  );
}