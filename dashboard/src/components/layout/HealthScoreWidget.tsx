import { useTranslation } from 'react-i18next';
import { useHealthScore } from '@/hooks/useCompliance';

export default function HealthScoreWidget() {
  const { t } = useTranslation();
  const { data, isLoading } = useHealthScore();

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg">
        <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" />
        <span className="text-xs text-gray-400">{t('common.loading')}</span>
      </div>
    );
  }

  const score = data?.score ?? 85;
  const scoreColor =
    score >= 80 ? 'text-status-ready' : score >= 60 ? 'text-status-review' : 'text-status-blocked';

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg">
      <div className={`w-2 h-2 rounded-full ${
        score >= 80 ? 'bg-status-ready' : score >= 60 ? 'bg-status-review' : 'bg-status-blocked'
      }`} />
      <span className={`text-xs font-semibold ${scoreColor}`}>{score}%</span>
      <span className="text-xs text-gray-400">{t('dashboard.healthScore')}</span>
    </div>
  );
}