import { useTranslation } from 'react-i18next';
import ComplianceTable from '@/components/ledger/ComplianceTable';

export default function Ledger() {
  const { t } = useTranslation();

  return (
    <div className="space-y-6 animate-slide-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('ledger.title')}</h1>
          <p className="text-sm text-gray-500 mt-1">{t('ledger.subtitle')}</p>
        </div>
        <button className="btn-primary flex items-center gap-2 text-sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          {t('ledger.exportResults')}
        </button>
      </div>

      {/* Compliance table */}
      <ComplianceTable />
    </div>
  );
}