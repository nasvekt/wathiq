import { useTranslation } from 'react-i18next';

interface ComplianceScoreRingProps {
  score: number;
  previousScore?: number;
  size?: number;
  strokeWidth?: number;
}

export default function ComplianceScoreRing({
  score,
  previousScore = 0,
  size = 160,
  strokeWidth = 10,
}: ComplianceScoreRingProps) {
  const { t } = useTranslation();

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  // Determine color based on score
  const getColor = () => {
    if (score >= 80) return '#3ECF8E';
    if (score >= 60) return '#F5A623';
    if (score >= 40) return '#F97316';
    return '#E53E3E';
  };

  const getBgColor = () => {
    if (score >= 80) return 'rgba(62, 207, 142, 0.15)';
    if (score >= 60) return 'rgba(245, 166, 35, 0.15)';
    if (score >= 40) return 'rgba(249, 115, 22, 0.15)';
    return 'rgba(229, 62, 62, 0.15)';
  };

  const change = score - previousScore;
  const changeDirection = change > 0 ? 'up' : change < 0 ? 'down' : 'stable';

  const getLabel = () => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Critical';
  };

  return (
    <div className="content-card p-5 flex flex-col items-center">
      <h3 className="text-sm font-medium text-gray-500 mb-4">{t('dashboard.healthScore')}</h3>

      <div className="relative" style={{ width: size, height: size }}>
        {/* Background ring */}
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={getBgColor()}
            strokeWidth={strokeWidth}
          />
          {/* Progress ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={getColor()}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color: getColor() }}>
            {score}%
          </span>
          <span className="text-xs text-gray-400 mt-1">{getLabel()}</span>
        </div>
      </div>

      {/* Change indicator */}
      <div className="flex items-center gap-1.5 mt-4 text-xs">
        <span className="text-gray-400">{t('dashboard.previousScore')}: {previousScore}%</span>
        <span className={`flex items-center gap-0.5 font-medium ${
          changeDirection === 'up' ? 'text-status-ready' : changeDirection === 'down' ? 'text-status-blocked' : 'text-gray-400'
        }`}>
          {changeDirection === 'up' && (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          )}
          {changeDirection === 'down' && (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          )}
          {change !== 0 && `${change > 0 ? '+' : ''}${change}%`}
        </span>
      </div>
    </div>
  );
}