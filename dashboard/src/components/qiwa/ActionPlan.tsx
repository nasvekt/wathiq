import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { qiwaApi } from '../../services/qiwa.service';

interface Props {
  data: any;
  onRetry: () => void;
}

const ActionPlan: React.FC<Props> = ({ data, onRetry }) => {
  const { t } = useTranslation();
  const [reportHtml, setReportHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const res = await qiwaApi.generateReport({
        scan_id: data.scan_id,
        company_name: data.company_name,
      });
      setReportHtml(res.data.html);
    } catch {
      alert(t('qiwaShield.reportError'));
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!reportHtml) return;
    const blob = new Blob([reportHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Wathiq-Rescue-Report-${data.scan_id}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* Executive Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('qiwaShield.rescuePlan')}</h2>
        
        {/* Score */}
        <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <span className="text-2xl font-bold text-primary">{data.compliance_health_score}</span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{t('qiwaShield.complianceHealth')}</p>
            <p className="text-xs text-gray-500">{t('qiwaShield.healthScoreDesc')}</p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-2xl font-bold text-gray-900">{data.undocumented_count}</p>
            <p className="text-xs text-gray-500">{t('qiwaShield.needDocs')}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-2xl font-bold text-amber-600">{data.at_risk_count}</p>
            <p className="text-xs text-gray-500">{t('qiwaShield.atRisk')}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-2xl font-bold text-red-600">{data.blocker_count}</p>
            <p className="text-xs text-gray-500">{t('qiwaShield.blockers')}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg text-center">
            <p className="text-2xl font-bold text-green-600">SAR {data.estimated_penalty_savings.toLocaleString()}</p>
            <p className="text-xs text-gray-500">{t('qiwaShield.potentialSavings')}</p>
          </div>
        </div>

        {/* Action Items */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">{t('qiwaShield.prioritizedActions')}</h3>
          <ol className="space-y-3">
            {data.action_items?.map((item: string, i: number) => (
              <li key={i} className="flex items-start gap-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <span className="w-6 h-6 rounded-full bg-amber-200 text-amber-800 flex items-center justify-center text-xs font-bold shrink-0">
                  {i + 1}
                </span>
                <p className="text-sm text-amber-900">{item}</p>
              </li>
            ))}
          </ol>
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm font-medium text-blue-900 mb-1">{t('qiwaShield.saudizationStatus')}</p>
            <p className="text-xs text-blue-700">
              {t('qiwaShield.saudizationDetail', {
                ratio: data.saudization_ratio,
                band: data.current_nitaqat_band,
              })}
            </p>
          </div>
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm font-medium text-purple-900 mb-1">{t('qiwaShield.penaltyExposure')}</p>
            <p className="text-xs text-purple-700">
              {t('qiwaShield.penaltyDetail', { amount: data.estimated_penalty_exposure?.toLocaleString() })}
            </p>
          </div>
        </div>
      </div>

      {/* Report Generation */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('qiwaShield.rescueReport')}</h2>
        <p className="text-sm text-gray-500 mb-4">{t('qiwaShield.rescueReportDesc')}</p>
        
        {!reportHtml ? (
          <button
            onClick={handleGenerateReport}
            disabled={loading}
            className="px-6 py-3 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-lg transition disabled:opacity-50"
          >
            {loading ? t('qiwaShield.generating') : t('qiwaShield.generatePdf')}
          </button>
        ) : (
          <div className="flex items-center gap-3">
            <button
              onClick={handleDownload}
              className="px-6 py-3 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-lg transition"
            >
              {t('qiwaShield.downloadReport')}
            </button>
            <button
              onClick={() => setReportHtml(null)}
              className="px-4 py-3 text-sm text-gray-600 hover:text-gray-800 transition"
            >
              {t('qiwaShield.regenerate')}
            </button>
          </div>
        )}
      </div>

      {/* New Scan */}
      <button
        onClick={onRetry}
        className="px-5 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
      >
        {t('qiwaShield.newScan')}
      </button>
    </div>
  );
};

export default ActionPlan;