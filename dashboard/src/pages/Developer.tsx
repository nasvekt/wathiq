import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function Developer() {
  const { t } = useTranslation();
  const [showKey, setShowKey] = useState(false);

  const apiKeys = [
    { id: '1', name: 'Production API Key', key_preview: 'wk_live_••••••••a3f8', created_at: '2026-01-15', last_used: '2026-04-28T14:32:00Z', active: true },
    { id: '2', name: 'Staging API Key', key_preview: 'wk_test_••••••••b2c1', created_at: '2026-02-20', last_used: '2026-04-27T09:15:00Z', active: true },
    { id: '3', name: 'CI/CD Integration Key', key_preview: 'wk_test_••••••••d4e7', created_at: '2026-03-10', last_used: null, active: false },
  ];

  return (
    <div className="space-y-6 animate-slide-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('developer.title')}</h1>
          <p className="text-sm text-gray-500 mt-1">{t('developer.subtitle')}</p>
        </div>
        <button className="btn-primary flex items-center gap-2 text-sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('developer.createKey')}
        </button>
      </div>

      {/* API Keys */}
      <div className="content-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700">{t('developer.apiKeys')}</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {apiKeys.map((key) => (
            <div key={key.id} className="px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-900">{key.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                    key.active
                      ? 'bg-status-ready/10 text-status-ready'
                      : 'bg-gray-100 text-gray-500'
                  }`}>
                    {key.active ? t('developer.active') : t('developer.inactive')}
                  </span>
                </div>
                <code className="text-xs font-mono text-gray-500 bg-gray-50 px-2 py-0.5 rounded">
                  {key.key_preview}
                </code>
                <div className="flex items-center gap-4 mt-1.5">
                  <span className="text-xs text-gray-400">
                    {t('developer.created')}: {key.created_at}
                  </span>
                  {key.last_used && (
                    <span className="text-xs text-gray-400">
                      {t('developer.lastUsed')}: {new Date(key.last_used).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <button className="btn-ghost text-xs flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                  </svg>
                  {t('developer.copyKey')}
                </button>
                <button className="text-xs text-status-blocked hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition-colors">
                  {t('developer.revoke')}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Endpoints */}
      <div className="content-card p-5">
        <h3 className="text-sm font-medium text-gray-500 mb-4">{t('developer.apiDocs')}</h3>
        <div className="space-y-2">
          {[
            { method: 'GET', path: '/api/compliance/dashboard', desc: 'Dashboard summary data' },
            { method: 'GET', path: '/api/compliance/employees', desc: 'Employee compliance records' },
            { method: 'POST', path: '/api/simulator/nitaqat', desc: 'Run Nitaqat simulation' },
            { method: 'POST', path: '/api/wage-sync/export', desc: 'Export SIF file' },
          ].map((ep, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                ep.method === 'GET' ? 'bg-status-ready/10 text-status-ready' : 'bg-primary/10 text-primary'
              }`}>
                {ep.method}
              </span>
              <code className="text-xs font-mono text-gray-700 flex-1">{ep.path}</code>
              <span className="text-xs text-gray-400">{ep.desc}</span>
            </div>
          ))}
        </div>
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <span className="text-xs text-gray-500">{t('developer.baseUrl')}:</span>
          <code className="text-xs font-mono text-gray-700 ml-2">https://api.wathiq.io/v1</code>
        </div>
      </div>
    </div>
  );
}