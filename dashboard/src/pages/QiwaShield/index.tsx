import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import FileUploader from '../../components/qiwa/FileUploader';
import ResultsDashboard from '../../components/qiwa/ResultsDashboard';
import NitaqatSimulator from '../../components/qiwa/NitaqatSimulator';
import ActionPlan from '../../components/qiwa/ActionPlan';
import { qiwaApi } from '../../services/qiwa.service';

const STEPS = ['Upload', 'Scan', 'Results', 'Simulate', 'Report'];

const QiwaShield: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRtl = i18n.language === 'ar';
  const [step, setStep] = useState(0);
  const [scanResult, setScanResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadMode, setUploadMode] = useState<'excel' | 'manual' | null>(null);

  const handleUpload = async (employees: any[], companyName?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await qiwaApi.upload({
        company_name: companyName || '',
        employees,
      });
      setScanResult(res.data);
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please check your data and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setStep(0);
    setScanResult(null);
    setError(null);
    setUploadMode(null);
  };

  return (
    <div className="min-h-screen bg-gray-50" dir={isRtl ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('qiwaShield.title')}</h1>
              <p className="text-sm text-gray-500">{t('qiwaShield.subtitle')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Stepper */}
      <div className="bg-white border-b border-gray-200 px-6">
        <div className="max-w-6xl mx-auto flex items-center gap-0 py-4">
          {STEPS.map((s, i) => (
            <React.Fragment key={s}>
              <div className={`flex items-center gap-2 ${i <= step ? 'text-primary' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  i < step ? 'bg-primary text-white' : i === step ? 'border-2 border-primary text-primary' : 'border-2 border-gray-300 text-gray-400'
                }`}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span className="text-sm font-medium hidden md:inline">{t(`qiwaShield.step${i}`)}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-px mx-3 ${i < step ? 'bg-primary' : 'bg-gray-300'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <svg className="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-800">{t('qiwaShield.errorTitle')}</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600">
              ✕
            </button>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin mb-4" />
            <p className="text-gray-600 font-medium">{t('qiwaShield.scanning')}</p>
            <p className="text-sm text-gray-400 mt-1">{t('qiwaShield.scanningDesc')}</p>
          </div>
        )}

        {!loading && step === 0 && (
          <div>
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <button
                onClick={() => setUploadMode('excel')}
                className={`p-8 rounded-2xl border-2 text-center transition ${
                  uploadMode === 'excel' ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{t('qiwaShield.uploadExcel')}</h3>
                <p className="text-sm text-gray-500">{t('qiwaShield.uploadExcelDesc')}</p>
              </button>
              <button
                onClick={() => setUploadMode('manual')}
                className={`p-8 rounded-2xl border-2 text-center transition ${
                  uploadMode === 'manual' ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{t('qiwaShield.manualEntry')}</h3>
                <p className="text-sm text-gray-500">{t('qiwaShield.manualEntryDesc')}</p>
              </button>
            </div>
            {uploadMode && <FileUploader mode={uploadMode} onSubmit={handleUpload} onBack={() => setUploadMode(null)} />}
          </div>
        )}

        {!loading && step === 2 && scanResult && <ResultsDashboard data={scanResult} onProceed={() => setStep(3)} />}
        {!loading && step === 3 && scanResult && (
          <NitaqatSimulator scanResult={scanResult} onProceed={() => setStep(4)} onBack={() => setStep(2)} />
        )}
        {!loading && step === 4 && scanResult && <ActionPlan data={scanResult} onRetry={handleRetry} />}
      </div>
    </div>
  );
};

export default QiwaShield;