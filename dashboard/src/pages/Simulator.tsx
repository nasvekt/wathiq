import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SECTOR_CODES } from '@/data/sector_codes';

export default function Simulator() {
  const { t } = useTranslation();
  const [expat, setExpat] = useState(100);
  const [saudi, setSaudi] = useState(15);
  const [targetExpat, setTargetExpat] = useState(80);
  const [targetSaudi, setTargetSaudi] = useState(25);
  const [industry, setIndustry] = useState('');

  const currentPercent = (saudi / (expat + saudi)) * 100;
  const targetPercent = (targetSaudi / (targetExpat + targetSaudi)) * 100;

  return (
    <div className="space-y-6 animate-slide-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('simulator.title')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('simulator.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Controls */}
        <div className="content-card p-6 space-y-5">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Workforce Parameters</h3>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('simulator.currentExpat')}: <span className="font-bold text-gray-900">{expat}</span>
            </label>
            <input
              type="range"
              min={0}
              max={500}
              value={expat}
              onChange={(e) => setExpat(Number(e.target.value))}
              className="w-full accent-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('simulator.currentSaudi')}: <span className="font-bold text-gray-900">{saudi}</span>
            </label>
            <input
              type="range"
              min={0}
              max={200}
              value={saudi}
              onChange={(e) => setSaudi(Number(e.target.value))}
              className="w-full accent-primary"
            />
          </div>

          <div className="border-t border-gray-100 pt-4">
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('simulator.targetExpat')}: <span className="font-bold text-gray-900">{targetExpat}</span>
            </label>
            <input
              type="range"
              min={0}
              max={500}
              value={targetExpat}
              onChange={(e) => setTargetExpat(Number(e.target.value))}
              className="w-full accent-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('simulator.targetSaudi')}: <span className="font-bold text-gray-900">{targetSaudi}</span>
            </label>
            <input
              type="range"
              min={0}
              max={200}
              value={targetSaudi}
              onChange={(e) => setTargetSaudi(Number(e.target.value))}
              className="w-full accent-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">
              {t('simulator.industry')}
            </label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="input-field"
            >
              <option value="">{t('simulator.selectIndustry')}</option>
              {SECTOR_CODES.map((s) => (
                <option key={s.code} value={s.code}>{s.name_en}</option>
              ))}
            </select>
          </div>

          <button className="btn-primary w-full">{t('simulator.simulate')}</button>
        </div>

        {/* Results */}
        <div className="content-card p-6 space-y-5">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Simulation Results</h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <span className="text-xs text-gray-500 block mb-1">{t('simulator.currentBand')}</span>
              <span className="text-lg font-bold text-gray-900">
                {currentPercent >= 15 ? 'High Green' : currentPercent >= 8 ? 'Low Green' : currentPercent >= 4 ? 'Yellow' : 'Red'}
              </span>
              <div className="mt-2 text-xs text-gray-400">{currentPercent.toFixed(1)}% Saudization</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <span className="text-xs text-gray-500 block mb-1">{t('simulator.projectedBand')}</span>
              <span className="text-lg font-bold text-gray-900">
                {targetPercent >= 15 ? 'High Green' : targetPercent >= 8 ? 'Low Green' : targetPercent >= 4 ? 'Yellow' : 'Red'}
              </span>
              <div className="mt-2 text-xs text-gray-400">{targetPercent.toFixed(1)}% Saudization</div>
            </div>
          </div>

          <div className="space-y-3 pt-2 border-t border-gray-100">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">{t('simulator.saudisNeeded')}</span>
              <span className="font-semibold">
                {targetSaudi > saudi ? targetSaudi - saudi : 0}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">{t('simulator.saudisSurplus')}</span>
              <span className="font-semibold">
                {saudi > targetSaudi ? saudi - targetSaudi : 0}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">{t('simulator.penaltyChange')}</span>
              <span className={`font-semibold ${targetPercent > currentPercent ? 'text-status-ready' : 'text-status-at-risk'}`}>
                {targetPercent > currentPercent ? '−' : '+'}SAR {(Math.abs(currentPercent - targetPercent) * 1250).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Visual bar */}
          <div className="pt-2">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span>Current: {currentPercent.toFixed(1)}%</span>
              <span>Target: {targetPercent.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 relative">
              <div
                className="h-2.5 rounded-full bg-primary absolute left-0 top-0 transition-all duration-500"
                style={{ width: `${Math.min(currentPercent * 3, 100)}%` }}
              />
              <div
                className="h-2.5 rounded-full bg-primary-dark absolute left-0 top-0 transition-all duration-500 opacity-40"
                style={{ width: `${Math.min(targetPercent * 3, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}