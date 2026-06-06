import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { qiwaApi } from '../../services/qiwa.service';

interface Props {
  scanResult: any;
  onProceed: () => void;
  onBack: () => void;
}

const BAND_COLORS: Record<string, string> = {
  platinum: '#E8D5B7', high_green: '#22C55E', low_green: '#86EFAC',
  yellow: '#EAB308', red: '#DC2626',
};

const BAND_ORDER = ['red', 'yellow', 'low_green', 'high_green', 'platinum'];

const NitaqatSimulator: React.FC<Props> = ({ scanResult, onProceed, onBack }) => {
  const { t } = useTranslation();
  const [addSaudi, setAddSaudi] = useState(0);
  const [simResult, setSimResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const currentBand = scanResult.current_nitaqat_band;
  const currentRatio = scanResult.saudization_ratio;

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const res = await qiwaApi.simulate({
          scan_id: scanResult.scan_id,
          add_saudi: addSaudi,
          add_saudi_documented: true,
        });
        setSimResult(res.data);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [addSaudi, scanResult.scan_id]);

  const projectedRatio = simResult?.projected_ratio ?? currentRatio;
  const projectedBand = simResult?.projected_band ?? currentBand;
  const currentBandIdx = BAND_ORDER.indexOf(currentBand);
  const projectedBandIdx = BAND_ORDER.indexOf(projectedBand);
  const improvement = projectedBandIdx > currentBandIdx;

  return (
    <div>
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('qiwaShield.simulatorTitle')}</h2>
        <p className="text-sm text-gray-500 mb-6">{t('qiwaShield.simulatorDesc')}</p>

        {/* Slider */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-gray-700">{t('qiwaShield.addSaudi')}</label>
            <span className="text-2xl font-bold text-primary">{addSaudi}</span>
          </div>
          <input
            type="range"
            min={0}
            max={50}
            value={addSaudi}
            onChange={(e) => setAddSaudi(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0</span><span>10</span><span>20</span><span>30</span><span>40</span><span>50</span>
          </div>
        </div>

        {/* Comparison */}
        {!loading && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-50 rounded-xl p-6">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">{t('qiwaShield.current')}</p>
              <p className="text-3xl font-bold mb-1" style={{ color: BAND_COLORS[currentBand] }}>
                {currentBand.toUpperCase()}
              </p>
              <p className="text-lg text-gray-600">{currentRatio.toFixed(1)}% {t('qiwaShield.saudization')}</p>
              <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(currentRatio, 100)}%`, backgroundColor: BAND_COLORS[currentBand] }} />
              </div>
            </div>
            <div className={`rounded-xl p-6 ${improvement ? 'bg-green-50 border-2 border-green-200' : 'bg-gray-50'}`}>
              <div className="flex items-center gap-2 mb-2">
                <p className="text-xs text-gray-500 uppercase tracking-wider">{t('qiwaShield.projected')}</p>
                {improvement && <span className="px-2 py-0.5 bg-green-200 text-green-800 text-xs font-medium rounded-full">+{simResult?.band_delta} band</span>}
              </div>
              <p className="text-3xl font-bold mb-1" style={{ color: BAND_COLORS[projectedBand] }}>
                {projectedBand.toUpperCase()}
              </p>
              <p className="text-lg text-gray-600">{projectedRatio.toFixed(1)}% {t('qiwaShield.saudization')}</p>
              <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(projectedRatio, 100)}%`, backgroundColor: BAND_COLORS[projectedBand] }} />
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        )}

        {/* Band Spectrum */}
        <div className="mb-8">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">{t('qiwaShield.nitaqatSpectrum')}</p>
          <div className="flex h-8 rounded-lg overflow-hidden">
            {BAND_ORDER.map((band) => {
              const isCurrent = band === currentBand;
              const isProjected = band === projectedBand && addSaudi > 0;
              return (
                <div key={band} className="flex-1 flex items-center justify-center relative" style={{ backgroundColor: BAND_COLORS[band] + '40' }}>
                  <span className="text-xs font-medium" style={{ color: BAND_COLORS[band] }}>
                    {band.replace('_', ' ').toUpperCase()}
                    {isCurrent && ' ←'}
                    {isProjected && ' ★'}
                  </span>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>Red (0-18%)</span>
            <span>Yellow (18-25%)</span>
            <span>Low Green (26-34%)</span>
            <span>High Green (35-39%)</span>
            <span>Platinum (40%+)</span>
          </div>
        </div>
      </div>

      {/* Action */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="px-5 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
          {t('common.back')}
        </button>
        <button
          onClick={onProceed}
          className="px-6 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-lg transition"
        >
          {t('qiwaShield.generateReport')}
        </button>
      </div>
    </div>
  );
};

export default NitaqatSimulator;