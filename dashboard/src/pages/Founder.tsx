import { useTranslation } from 'react-i18next';

export default function Founder() {
  const { t } = useTranslation();

  const stats = [
    { label: 'Active Companies', value: '47', change: '+3', icon: '🏢' },
    { label: 'Total Employees Tracked', value: '86,421', change: '+2,147', icon: '👥' },
    { label: 'Compliance Checks Today', value: '12,483', change: '+892', icon: '✅' },
    { label: 'System Health', value: '99.8%', change: '+0.2%', icon: '📊' },
  ];

  return (
    <div className="space-y-6 animate-slide-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('nav.founder')}</h1>
        <p className="text-sm text-gray-500 mt-1">Administrative dashboard for platform oversight</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="content-card p-5">
            <span className="text-2xl block mb-2">{stat.icon}</span>
            <span className="text-xs text-gray-500 block mb-1">{stat.label}</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
              <span className="text-xs text-status-ready font-medium">{stat.change}</span>
            </div>
          </div>
        ))}
      </div>

      {/* User list */}
      <div className="content-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700">Registered Companies</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">Company</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">Industry</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">Size</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">Status</th>
              <th className="text-right text-xs font-medium text-gray-500 uppercase tracking-wider px-5 py-3">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {[
              { name: 'Almosaikah Trading Co.', industry: 'Retail', size: '250-500', status: 'active', joined: 'Jan 2026' },
              { name: 'Saudi Tech Solutions', industry: 'Technology', size: '100-250', status: 'active', joined: 'Feb 2026' },
              { name: 'Gulf Construction Group', industry: 'Construction', size: '500+', status: 'active', joined: 'Feb 2026' },
              { name: 'Alfaisal Medical Center', industry: 'Healthcare', size: '100-250', status: 'trial', joined: 'Apr 2026' },
            ].map((company, i) => (
              <tr key={i} className="hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3 text-sm font-medium text-gray-900">{company.name}</td>
                <td className="px-5 py-3 text-sm text-gray-600">{company.industry}</td>
                <td className="px-5 py-3 text-sm text-gray-600">{company.size}</td>
                <td className="px-5 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    company.status === 'active'
                      ? 'bg-status-ready/10 text-status-ready'
                      : 'bg-status-review/10 text-status-review'
                  }`}>
                    {company.status}
                  </span>
                </td>
                <td className="px-5 py-3 text-sm text-gray-500 text-right">{company.joined}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}