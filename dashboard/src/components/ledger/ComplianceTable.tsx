import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useEmployees } from '@/hooks/useCompliance';
import { useLanguage } from '@/hooks/useLanguage';
import StatusBadge from './StatusBadge';
import type { Employee } from '@/types/employee';

export default function ComplianceTable() {
  const { t } = useTranslation();
  const { isRTL } = useLanguage();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useEmployees({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: 25,
  });

  const employees: Employee[] = data?.employees ?? data ?? [];
  const total = data?.total ?? data?.total_employees ?? 0;
  const totalPages = Math.ceil(total / 25);

  const formatSalary = (value: number) =>
    new Intl.NumberFormat('en-SA', { style: 'currency', currency: 'SAR', minimumFractionDigits: 0 }).format(value);

  return (
    <div className="content-card overflow-hidden">
      {/* Filters */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="flex-1 relative">
            <svg
              className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 ${isRTL ? 'right-3' : 'left-3'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder={t('ledger.search')}
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className={`input-field ${isRTL ? 'pr-10' : 'pl-10'}`}
            />
          </div>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="input-field w-full sm:w-44"
          >
            <option value="">{t('ledger.allStatuses')}</option>
            <option value="ready">{t('dashboard.ready')}</option>
            <option value="review">{t('dashboard.review')}</option>
            <option value="blocked">{t('dashboard.blocked')}</option>
            <option value="at_risk">{t('dashboard.atRisk')}</option>
            <option value="pending">{t('dashboard.pending')}</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-gray-400">{t('common.loading')}</p>
          </div>
        ) : error ? (
          <div className="p-12 text-center">
            <p className="text-sm text-status-blocked">{t('common.error')}</p>
          </div>
        ) : employees.length === 0 ? (
          <div className="p-12 text-center">
            <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-sm text-gray-500">{t('ledger.noResults')}</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50">
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.employee')}
                </th>
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.iqama')}
                </th>
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.status')}
                </th>
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.nationality')}
                </th>
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.jobTitle')}
                </th>
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.salary')}
                </th>
                <th className={`text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3 ${isRTL ? 'text-right' : ''}`}>
                  {t('ledger.nitaqatWeight')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {employees.map((employee: Employee) => (
                <tr
                  key={employee.id}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-gray-900">
                      {employee.name_en}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-mono text-gray-600">{employee.iqama}</span>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={employee.status} size="sm" />
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-gray-600">{employee.nationality}</span>
                  </td>
                  <td className="px-4 py-3 max-w-[200px]">
                    <span className="text-sm text-gray-600 truncate block">{employee.job_title}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-gray-900">
                      {formatSalary(employee.gross_salary)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-gray-600">{employee.nitaqat_weight}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50">
          <span className="text-xs text-gray-500">
            {t('ledger.totalEmployees')}: {total}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t('common.previous')}
            </button>
            <span className="text-xs text-gray-500">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t('common.next')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}