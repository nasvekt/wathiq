import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { SECTOR_CODES } from '@/data/sector_codes';

export default function Onboarding() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    employee_count: '',
    bank: '',
    sector: '',
    accept_terms: false,
  });

  const steps = [
    { title: 'Company Profile', icon: '🏢' },
    { title: 'Payroll Setup', icon: '💳' },
    { title: 'Review & Start', icon: '🚀' },
  ];

  const handleComplete = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-lg">
        {/* Brand */}
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">و</span>
          </div>
          <h1 className="text-white font-bold text-xl">{t('app.name')}</h1>
        </div>

        <h2 className="text-white text-2xl font-bold text-center mb-1">{t('auth.completeSetup')}</h2>
        <p className="text-gray-400 text-sm text-center mb-8">
          Configure your compliance workspace in a few steps
        </p>

        {/* Step indicators */}
        <div className="flex items-center justify-center gap-2 mb-10">
          {steps.map((s, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-all ${
                step === i + 1 ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-gray-800 text-gray-500'
              }`}>
                <span>{s.icon}</span>
                <span className="hidden sm:inline">{s.title}</span>
              </div>
              {i < steps.length - 1 && <span className="text-gray-600 text-xs">→</span>}
            </div>
          ))}
        </div>

        {/* Step 1: Company Profile */}
        {step === 1 && (
          <div className="bg-surface-card border border-gray-800 rounded-xl p-6 space-y-4">
            <h3 className="text-white font-semibold text-lg">Company Information</h3>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Industry Sector</label>
              <select
                value={form.sector}
                onChange={(e) => setForm({ ...form, sector: e.target.value })}
                className="w-full px-4 py-2.5 bg-surface-base border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
              >
                <option value="">Select your industry</option>
                {SECTOR_CODES.map((s) => (
                  <option key={s.code} value={s.code}>{s.name_en}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Total Employees</label>
              <input
                type="number"
                value={form.employee_count}
                onChange={(e) => setForm({ ...form, employee_count: e.target.value })}
                placeholder="e.g. 250"
                className="w-full px-4 py-2.5 bg-surface-base border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
              />
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!form.sector || !form.employee_count}
              className="btn-primary w-full mt-2 disabled:opacity-40"
            >
              Next Step →
            </button>
          </div>
        )}

        {/* Step 2: Payroll Setup */}
        {step === 2 && (
          <div className="bg-surface-card border border-gray-800 rounded-xl p-6 space-y-4">
            <h3 className="text-white font-semibold text-lg">Payroll Configuration</h3>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Primary Bank</label>
              <select
                value={form.bank}
                onChange={(e) => setForm({ ...form, bank: e.target.value })}
                className="w-full px-4 py-2.5 bg-surface-base border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
              >
                <option value="">Select your bank</option>
                <option value="10">National Commercial Bank</option>
                <option value="40">Al Rajhi Bank</option>
                <option value="20">Riyad Bank</option>
                <option value="80">Bank AlJazira</option>
              </select>
            </div>

            <div className="p-4 bg-gray-900 rounded-lg border border-gray-700">
              <p className="text-sm text-gray-300">
                Wathiq will automatically validate your payroll data against:
              </p>
              <ul className="mt-2 space-y-1 text-xs text-gray-400">
                <li>• GOSI enrollment records</li>
                <li>• WPS salary floor compliance</li>
                <li>• Nitaqat Saudization quotas</li>
                <li>• Iqama and contract validity</li>
              </ul>
            </div>

            <div className="flex gap-3">
              <button onClick={() => setStep(1)} className="btn-ghost text-gray-300 border border-gray-700 flex-1">
                ← Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="btn-primary flex-1"
              >
                Review →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Review & Start */}
        {step === 3 && (
          <div className="bg-surface-card border border-gray-800 rounded-xl p-6 space-y-4">
            <h3 className="text-white font-semibold text-lg">Ready to Launch</h3>

            <div className="space-y-3">
              {[
                { label: 'Industry', value: SECTOR_CODES.find((s) => s.code === form.sector)?.name_en || form.sector },
                { label: 'Employees', value: form.employee_count },
                { label: 'Bank', value: form.bank === '10' ? 'National Commercial Bank' : form.bank === '40' ? 'Al Rajhi Bank' : `Code ${form.bank}` },
                { label: 'Plan', value: 'Business — SAR 299/month' },
              ].map((item) => (
                <div key={item.label} className="flex justify-between text-sm py-2 border-b border-gray-700 last:border-0">
                  <span className="text-gray-400">{item.label}</span>
                  <span className="text-white font-medium">{item.value}</span>
                </div>
              ))}
            </div>

            <label className="flex items-center gap-3 cursor-pointer mt-4">
              <input
                type="checkbox"
                checked={form.accept_terms}
                onChange={(e) => setForm({ ...form, accept_terms: e.target.checked })}
                className="w-4 h-4 rounded border-gray-600 bg-surface-base text-primary focus:ring-primary"
              />
              <span className="text-sm text-gray-300">
                I agree to the{' '}
                <a href="#" className="text-primary hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-primary hover:underline">Privacy Policy</a>
              </span>
            </label>

            <div className="flex gap-3 mt-2">
              <button onClick={() => setStep(2)} className="btn-ghost text-gray-300 border border-gray-700 flex-1">
                ← Back
              </button>
              <button
                onClick={handleComplete}
                disabled={!form.accept_terms}
                className="btn-primary flex-1 disabled:opacity-40"
              >
                Launch Dashboard 🚀
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}