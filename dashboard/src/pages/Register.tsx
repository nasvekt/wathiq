import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useRegister } from '@/hooks/useAuth';
import { SECTOR_CODES } from '@/data/sector_codes';

export default function Register() {
  const { t } = useTranslation();
  const registerMutation = useRegister();

  const [form, setForm] = useState({
    email: '',
    password: '',
    confirm_password: '',
    company_name: '',
    industry: '',
    company_size: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    registerMutation.mutate({
      email: form.email,
      password: form.password,
      company_name: form.company_name,
      industry: form.industry,
      company_size: form.company_size,
    });
  };

  return (
    <div className="min-h-screen bg-surface-base flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">و</span>
          </div>
          <div>
            <h1 className="text-white font-bold text-xl">{t('app.name')}</h1>
            <p className="text-gray-500 text-xs">{t('app.tagline')}</p>
          </div>
        </div>

        <h2 className="text-white text-2xl font-bold text-center mb-2">{t('auth.createAccount')}</h2>
        <p className="text-gray-400 text-sm text-center mb-8">{t('auth.registerSubtitle')}</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">{t('auth.companyName')}</label>
            <input
              type="text"
              value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })}
              placeholder="Your Company Ltd."
              required
              className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">{t('auth.email')}</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@company.com"
              required
              className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">{t('auth.industry')}</label>
              <select
                value={form.industry}
                onChange={(e) => setForm({ ...form, industry: e.target.value })}
                required
                className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
              >
                <option value="">Select</option>
                {SECTOR_CODES.map((s) => (
                  <option key={s.code} value={s.code}>{s.name_en}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">{t('auth.companySize')}</label>
              <select
                value={form.company_size}
                onChange={(e) => setForm({ ...form, company_size: e.target.value })}
                required
                className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
              >
                <option value="">Select</option>
                <option value="1-49">1–49</option>
                <option value="50-249">50–249</option>
                <option value="250-499">250–499</option>
                <option value="500+">500+</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">{t('auth.password')}</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="At least 8 characters"
              required
              minLength={8}
              className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">{t('auth.confirmPassword')}</label>
            <input
              type="password"
              value={form.confirm_password}
              onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
              placeholder="Confirm your password"
              required
              minLength={8}
              className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary text-sm"
            />
          </div>

          {registerMutation.isError && (
            <div className="p-3 bg-status-blocked/10 border border-status-blocked/20 rounded-lg">
              <p className="text-status-blocked text-xs">{(registerMutation.error as any)?.response?.data?.detail || t('common.error')}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={registerMutation.isPending}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {registerMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                {t('common.loading')}
              </>
            ) : (
              t('auth.signUp')
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          {t('auth.hasAccount')}{' '}
          <a href="/login" className="text-primary hover:text-primary-dark font-medium">
            {t('auth.signIn')}
          </a>
        </p>
      </div>
    </div>
  );
}