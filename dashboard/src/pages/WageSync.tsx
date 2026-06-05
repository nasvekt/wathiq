import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function WageSync() {
  const { t } = useTranslation();
  const [batchId, setBatchId] = useState('');
  const [includeAll, setIncludeAll] = useState(true);

  return (
    <div className="space-y-6 animate-slide-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('wageSync.title')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('wageSync.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Export form */}
        <div className="content-card p-6 space-y-5">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Export Configuration</h3>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('wageSync.selectBatch')}
            </label>
            <select
              value={batchId}
              onChange={(e) => setBatchId(e.target.value)}
              className="input-field"
            >
              <option value="">— Select a batch —</option>
              <option value="batch-001">Batch #1243 — Apr 2026</option>
              <option value="batch-002">Batch #1242 — Mar 2026</option>
              <option value="batch-003">Batch #1241 — Feb 2026</option>
            </select>
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={includeAll}
              onChange={(e) => setIncludeAll(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <span className="text-sm text-gray-700">{t('wageSync.includeAll')}</span>
          </label>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('wageSync.statusFilter')}
            </label>
            <select disabled={includeAll} className="input-field opacity-50 disabled:cursor-not-allowed">
              <option value="">All Statuses</option>
              <option value="ready">Ready</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>

          <button
            disabled={!batchId}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            {t('wageSync.exportSif')}
          </button>
        </div>

        {/* Info panel */}
        <div className="content-card p-6 space-y-5">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">SIF Format Info</h3>

          <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-800">SIF File Format</p>
                <p className="text-xs text-blue-600 mt-1">
                  Saudi Arabian Monetary Authority (SAMA) compliant wage file format for bank salary transfers.
                  Includes employee Iqama, bank code, account number, salary amount, and transfer date.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm py-2 border-b border-gray-100">
              <span className="text-gray-500">{t('wageSync.lastGenerated')}</span>
              <span className="text-gray-900 font-medium">Apr 28, 2026 — 14:32 AST</span>
            </div>
            <div className="flex justify-between text-sm py-2 border-b border-gray-100">
              <span className="text-gray-500">{t('wageSync.recordsIncluded')}</span>
              <span className="text-gray-900 font-medium">1,842 records</span>
            </div>
            <div className="flex justify-between text-sm py-2">
              <span className="text-gray-500">Format</span>
              <span className="text-gray-900 font-mono font-medium text-xs bg-gray-100 px-2 py-0.5 rounded">SIF v3.2</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}