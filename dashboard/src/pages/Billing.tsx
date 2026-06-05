import { useTranslation } from 'react-i18next';

export default function Billing() {
  const { t } = useTranslation();

  const invoices = [
    { id: 'INV-001', amount: 299, status: 'paid', date: '2026-04-01' },
    { id: 'INV-002', amount: 299, status: 'paid', date: '2026-03-01' },
    { id: 'INV-003', amount: 299, status: 'pending', date: '2026-05-01' },
  ];

  return (
    <div className="space-y-6 animate-slide-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('billing.title')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('billing.subtitle')}</p>
      </div>

      {/* Plan overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="content-card p-5">
          <span className="text-xs text-gray-500 block mb-1">{t('billing.currentPlan')}</span>
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-gray-900">Business</span>
            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium">Active</span>
          </div>
          <span className="text-sm text-gray-400 mt-1 block">SAR 299/month</span>
        </div>
        <div className="content-card p-5">
          <span className="text-xs text-gray-500 block mb-1">{t('billing.creditsUsed')}</span>
          <span className="text-xl font-bold text-gray-900">1,842</span>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
            <div className="bg-primary h-1.5 rounded-full" style={{ width: '37%' }} />
          </div>
        </div>
        <div className="content-card p-5">
          <span className="text-xs text-gray-500 block mb-1">{t('billing.creditsTotal')}</span>
          <span className="text-xl font-bold text-gray-900">5,000</span>
          <span className="text-sm text-gray-400 mt-1 block">{t('billing.nextBilling')}: May 1, 2026</span>
        </div>
      </div>

      {/* Invoices */}
      <div className="content-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700">{t('billing.invoices')}</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">{t('billing.date')}</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">{t('billing.amount')}</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">{t('billing.status')}</th>
              <th className="text-right text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">{t('billing.download')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {invoices.map((inv) => (
              <tr key={inv.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3 text-sm text-gray-900">{inv.date}</td>
                <td className="px-5 py-3 text-sm font-medium text-gray-900">SAR {inv.amount}</td>
                <td className="px-5 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    inv.status === 'paid' ? 'bg-status-ready/10 text-status-ready' : 'bg-status-review/10 text-status-review'
                  }`}>
                    {inv.status}
                  </span>
                </td>
                <td className="px-5 py-3 text-right">
                  <button className="text-xs text-primary hover:text-primary-dark font-medium">
                    PDF
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}