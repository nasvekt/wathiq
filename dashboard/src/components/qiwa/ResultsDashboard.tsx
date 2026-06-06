import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface Props {
  data: any;
  onProceed: () => void;
}

const ResultsDashboard: React.FC<Props> = ({ data, onProceed }) => {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<'all' | 'undocumented' | 'documented' | 'at_risk'>('all');
  const [search, setSearch] = useState('');

  const bandColors: Record<string, string> = {
    platinum: '#E8D5B7', high_green: '#22C55E', low_green: '#86EFAC',
    yellow: '#EAB308', red: '#DC2626',
  };
  const bandColor = bandColors[data.current_nitaqat_band] || '#6B7280';

  const score = data.compliance_health_score;
  const employees = data.employees || [];

  const filtered = employees.filter((e: any) => {
    if (filter === 'undocumented' && e.document_status !== 'missing' && e.document_status !== 'at_risk') return false;
    if (filter === 'documented' && e.document_status !== 'documented') return false;
    if (filter === 'at_risk' && e.document_status !== 'at_risk') return false;
    if (search && !e.employee_name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div>
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{t('qiwaShield.totalEmployees')}</p>
          <p className="text-3xl font-bold text-gray-900">{data.total_employees}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{t('qiwaShield.documented')}</p>
          <p className="text-3xl font-bold text-green-600">{data.documented_count}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{t('qiwaShield.undocumented')}</p>
          <p className="text-3xl font-bold text-amber-600">{data.undocumented_count}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{t('qiwaShield.atRisk')}</p>
          <p className="text-3xl font-bold text-red-600">{data.at_risk_count}</p>
        </div>
      </div>

      {/* Health Score + Band */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 flex items-center gap-6">
          <div className="relative w-24 h-24">
            <svg className="w-24 h-24 -rotate-90" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="none" stroke="#E5E7EB" strokeWidth="3" />
              <circle cx="18" cy="18" r="16" fill="none" stroke={bandColor} strokeWidth="3"
                strokeDasharray={`${score * 2.01} 100`} strokeLinecap="round" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold" style={{ color: bandColor }}>{score}</span>
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{t('qiwaShield.complianceHealth')}</p>
            <p className="text-xs text-gray-500 mt-1">{t('qiwaShield.healthDesc')}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-2">{t('qiwaShield.nitaqatBand')}</p>
          <div className="flex items-center gap-3">
            <span className="text-3xl font-bold" style={{ color: bandColor }}>{data.current_nitaqat_band.toUpperCase()}</span>
            <span className="text-lg text-gray-600">{data.saudization_ratio.toFixed(1)}% {t('qiwaShield.saudization')}</span>
          </div>
          <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full rounded-full" style={{ width: `${Math.min(data.saudization_ratio, 100)}%`, backgroundColor: bandColor }} />
          </div>
        </div>
      </div>

      {/* Employee Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-8">
        <div className="p-4 border-b border-gray-100 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            {['all', 'undocumented', 'documented', 'at_risk'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as any)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg transition ${
                  filter === f ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {t(`qiwaShield.filter${f.charAt(0).toUpperCase() + f.slice(1)}`)}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('qiwaShield.searchEmployees')}
            className="ml-auto px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:border-primary outline-none w-48"
          />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.name')}</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">IQAMA</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.status')}</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.forSaudization')}</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.weight')}</th>
                <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.issues')}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.filter((e: any) => e.is_saudi).map((emp: any, i: number) => {
                const docColor = emp.document_status === 'documented' ? '#3ECF8E' :
                  emp.document_status === 'at_risk' ? '#E53E3E' : '#F5A623';
                return (
                  <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{emp.employee_name}</td>
                    <td className="px-4 py-3 text-gray-500">{emp.iqama_number}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                        style={{ backgroundColor: `${docColor}15`, color: docColor }}>
                        <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: docColor }} />
                        {emp.document_status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">{emp.can_count_for_saudization ? '✅' : '❌'}</td>
                    <td className="px-4 py-3">{emp.nitaqat_weight}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        emp.violations.length === 0 ? 'bg-green-100 text-green-700' :
                        emp.violations.length > 2 ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                      }`}>
                        {emp.violations.length} {emp.violations.length === 1 ? 'issue' : 'issues'}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {filtered.filter((e: any) => e.is_saudi).length === 0 && (
                <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">{t('qiwaShield.noResults')}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action */}
      <div className="flex items-center gap-3">
        <button
          onClick={onProceed}
          className="px-6 py-3 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-lg transition"
        >
          {t('qiwaShield.simulateNitaqat')}
        </button>
      </div>
    </div>
  );
};

export default ResultsDashboard;