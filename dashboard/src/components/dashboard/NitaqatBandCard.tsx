import { useTranslation } from 'react-i18next';
import type { NitaqatBand } from '@/types/employee';

interface NitaqatBandCardProps {
  band: NitaqatBand;
  percentage: number;
  saudiCount?: number;
  expatCount?: number;
}

const bandConfig: Record<NitaqatBand, { label: string; color: string; bgColor: string; borderColor: string }> = {
  platinum: {
    label: 'Platinum',
    color: '#E8D5B7',
    bgColor: 'rgba(232, 213, 183, 0.1)',
    borderColor: 'rgba(232, 213, 183, 0.3)',
  },
  high_green: {
    label: 'High Green',
    color: '#22C55E',
    bgColor: 'rgba(34, 197, 94, 0.1)',
    borderColor: 'rgba(34, 197, 94, 0.3)',
  },
  low_green: {
    label: 'Low Green',
    color: '#86EFAC',
    bgColor: 'rgba(134, 239, 172, 0.1)',
    borderColor: 'rgba(134, 239, 172, 0.3)',
  },
  yellow: {
    label: 'Yellow',
    color: '#EAB308',
    bgColor: 'rgba(234, 179, 8, 0.1)',
    borderColor: 'rgba(234, 179, 8, 0.3)',
  },
  red: {
    label: 'Red',
    color: '#DC2626',
    bgColor: 'rgba(220, 38, 38, 0.1)',
    borderColor: 'rgba(220, 38, 38, 0.3)',
  },
};

export default function NitaqatBandCard({
  band,
  percentage,
  saudiCount = 0,
  expatCount = 0,
}: NitaqatBandCardProps) {
  const { t } = useTranslation();
  const config = bandConfig[band] || bandConfig.red;
  const total = saudiCount + expatCount;
  const saudiPercent = total > 0 ? (saudiCount / total) * 100 : 0;

  return (
    <div className="content-card p-5">
      <h3 className="text-sm font-medium text-gray-500 mb-4">{t('dashboard.nitaqatBand')}</h3>

      {/* Band badge */}
      <div
        className="inline-flex items-center gap-2 px-4 py-2 rounded-lg mb-4"
        style={{
          backgroundColor: config.bgColor,
          borderColor: config.borderColor,
          border: '1px solid',
        }}
      >
        <span
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: config.color }}
        />
        <span className="font-semibold text-sm" style={{ color: config.color }}>
          {config.label}
        </span>
      </div>

      {/* Percentage */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs text-gray-400">{t('dashboard.nitaqatPercentage')}</span>
          <span className="text-sm font-semibold" style={{ color: config.color }}>
            {percentage.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-500"
            style={{
              width: `${Math.min(percentage, 100)}%`,
              backgroundColor: config.color,
            }}
          />
        </div>
      </div>

      {/* Workforce breakdown */}
      <div className="grid grid-cols-2 gap-4 pt-3 border-t border-gray-100">
        <div>
          <span className="text-xs text-gray-400 block">{t('dashboard.saudiWorkforce')}</span>
          <span className="text-lg font-semibold text-gray-900">{saudiCount}</span>
          <span className="text-xs text-gray-400 ml-1">({saudiPercent.toFixed(0)}%)</span>
        </div>
        <div>
          <span className="text-xs text-gray-400 block">{t('dashboard.expatWorkforce')}</span>
          <span className="text-lg font-semibold text-gray-900">{expatCount}</span>
          <span className="text-xs text-gray-400 ml-1">({(100 - saudiPercent).toFixed(0)}%)</span>
        </div>
      </div>
    </div>
  );
}