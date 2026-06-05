import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '@/hooks/useLanguage';
import { useLogin } from '@/hooks/useAuth';

export default function Login() {
  const { t } = useTranslation();
  const { isRTL } = useLanguage();
  const loginMutation = useLogin();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate({ email, password });
  };

  return (
    <div className="min-h-screen bg-surface-base flex">
      {/* Left side — branding panel */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-surface-base via-surface-card to-surface-base overflow-hidden">
        {/* Decorative grid */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(62, 207, 142, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(62, 207, 142, 0.3) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
        {/* Glowing orb */}
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-primary/10 blur-[100px]" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-primary/5 blur-[100px]" />

        <div className="relative z-10 flex flex-col justify-center px-16">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
              <span className="text-white font-bold text-xl">و</span>
            </div>
            <div>
              <h1 className="text-white font-bold text-2xl">{t('app.name')}</h1>
              <p className="text-gray-400 text-sm">{t('app.tagline')}</p>
            </div>
          </div>

          <h2 className="text-white text-4xl font-bold leading-tight mb-4">
            {t('auth.welcomeBack')}
          </h2>
          <p className="text-gray-400 text-lg leading-relaxed max-w-md">
            {t('auth.loginSubtitle')}
          </p>

          {/* Feature list */}
          <div className="mt-10 space-y-4">
            {[
              { icon: '🛡️', text: 'Real-time compliance monitoring' },
              { icon: '📊', text: 'Nitaqat band tracking & simulation' },
              { icon: '📋', text: 'Automated SIF file generation' },
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-lg">{feature.icon}</span>
                <span className="text-gray-300 text-sm">{feature.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right side — login form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Mobile brand */}
          <div className="flex items-center gap-3 mb-8 lg:hidden">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">و</span>
            </div>
            <div>
              <h1 className="text-white font-bold text-xl">{t('app.name')}</h1>
              <p className="text-gray-500 text-xs">{t('app.tagline')}</p>
            </div>
          </div>

          <h2 className="text-white text-2xl font-bold mb-2">{t('auth.login')}</h2>
          <p className="text-gray-400 text-sm mb-8">{t('auth.loginSubtitle')}</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                {t('auth.email')}
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200 text-sm"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-medium text-gray-300">
                  {t('auth.password')}
                </label>
                <button type="button" className="text-xs text-primary hover:text-primary-dark transition-colors">
                  {t('auth.forgotPassword')}
                </button>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2.5 bg-surface-card border border-gray-700 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all duration-200 text-sm"
              />
            </div>

            {loginMutation.isError && (
              <div className="p-3 bg-status-blocked/10 border border-status-blocked/20 rounded-lg">
                <p className="text-status-blocked text-xs">
                  {(loginMutation.error as any)?.response?.data?.detail || t('common.error')}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loginMutation.isPending}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {loginMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {t('common.loading')}
                </>
              ) : (
                t('auth.signIn')
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            {t('auth.noAccount')}{' '}
            <a href="/register" className="text-primary hover:text-primary-dark font-medium">
              {t('auth.signUp')}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}