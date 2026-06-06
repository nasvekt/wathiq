import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

interface Props {
  mode: 'excel' | 'manual';
  onSubmit: (employees: any[], companyName?: string) => void;
  onBack: () => void;
}

const SAMPLE_EMPLOYEE = {
  employee_name: '',
  employee_name_ar: '',
  iqama_number: '',
  nationality: 'Saudi Arabia',
  is_saudi: true,
  basic_salary: 4000,
  total_gross_wage: 4000,
  job_title: '',
  contract_documented_in_qiwa: false,
  gosi_enrolled: true,
  monthly_hours: 0,
};

const FileUploader: React.FC<Props> = ({ mode, onSubmit, onBack }) => {
  const { t } = useTranslation();
  const [employees, setEmployees] = useState<any[]>([{ ...SAMPLE_EMPLOYEE, ref_id: 'emp-001' }]);
  const [companyName, setCompanyName] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const addRow = () => {
    setEmployees([...employees, { ...SAMPLE_EMPLOYEE, ref_id: `emp-${(employees.length + 1).toString().padStart(3, '0')}` }]);
  };

  const updateRow = (index: number, field: string, value: any) => {
    const updated = [...employees];
    (updated[index] as any)[field] = value;
    if (field === 'basic_salary' || field === 'total_gross_wage') {
      const basic = field === 'basic_salary' ? Number(value) : Number(updated[index].basic_salary);
      const total = field === 'total_gross_wage' ? Number(value) : Number(updated[index].total_gross_wage);
      updated[index].total_gross_wage = Math.max(total, basic);
    }
    setEmployees(updated);
  };

  const removeRow = (index: number) => {
    if (employees.length > 1) {
      setEmployees(employees.filter((_, i) => i !== index));
    }
  };

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    // In production: parse xlsx/csv with SheetJS
    alert(t('qiwaShield.fileParseComing'));
  }, [t]);

  const handleSubmit = () => {
    if (!employees.length) return;
    onSubmit(employees, companyName);
  };

  if (mode === 'excel') {
    return (
      <div>
        <div
          onDrop={handleFileDrop}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition mb-4 ${
            dragOver ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-gray-400 bg-white'
          }`}
        >
          <svg className="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-gray-600 font-medium mb-1">{t('qiwaShield.dragDrop')}</p>
          <p className="text-sm text-gray-400">{t('qiwaShield.supportedFormats')}</p>
        </div>
        <div className="flex items-center gap-3 mt-4">
          <button onClick={onBack} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg transition">
            {t('common.back')}
          </button>
          <button onClick={() => alert(t('qiwaShield.sampleDownloadComing'))} className="px-4 py-2 text-sm text-primary hover:text-primary-dark font-medium transition">
            {t('qiwaShield.downloadSample')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="bg-white rounded-2xl border border-gray-200 p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">{t('qiwaShield.companyName')}</label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            placeholder={t('qiwaShield.companyNamePlaceholder')}
          />
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">#</th>
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.name')}</th>
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">IQAMA</th>
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.salary')}</th>
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.qiwaDoc')}</th>
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">GOSI</th>
                <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase"></th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp, i) => (
                <tr key={i} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-3 py-2 text-gray-400 text-xs">{i + 1}</td>
                  <td className="px-3 py-2">
                    <input
                      value={emp.employee_name}
                      onChange={(e) => updateRow(i, 'employee_name', e.target.value)}
                      className="w-32 px-2 py-1 border border-gray-200 rounded text-sm focus:border-primary outline-none"
                      placeholder="Name"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      value={emp.iqama_number}
                      onChange={(e) => updateRow(i, 'iqama_number', e.target.value)}
                      className="w-28 px-2 py-1 border border-gray-200 rounded text-sm focus:border-primary outline-none"
                      placeholder="IQAMA"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      value={emp.basic_salary}
                      onChange={(e) => updateRow(i, 'basic_salary', e.target.value)}
                      className="w-24 px-2 py-1 border border-gray-200 rounded text-sm focus:border-primary outline-none"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={emp.contract_documented_in_qiwa}
                        onChange={(e) => updateRow(i, 'contract_documented_in_qiwa', e.target.checked)}
                        className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                      />
                      <span className="text-xs text-gray-500">{t('qiwaShield.documented')}</span>
                    </label>
                  </td>
                  <td className="px-3 py-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={emp.gosi_enrolled}
                        onChange={(e) => updateRow(i, 'gosi_enrolled', e.target.checked)}
                        className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                      />
                      <span className="text-xs text-gray-500">{t('qiwaShield.enrolled')}</span>
                    </label>
                  </td>
                  <td className="px-3 py-2">
                    <button onClick={() => removeRow(i)} className="text-gray-400 hover:text-red-500 transition">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center gap-3 mt-4">
          <button onClick={addRow} className="flex items-center gap-2 text-sm text-primary hover:text-primary-dark font-medium transition">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            {t('qiwaShield.addEmployee')}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3 mt-6">
        <button onClick={onBack} className="px-5 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
          {t('common.back')}
        </button>
        <button
          onClick={handleSubmit}
          disabled={!employees.some(e => e.employee_name)}
          className="px-6 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {t('qiwaShield.scanEmployees')}
        </button>
      </div>
    </div>
  );
};

export default FileUploader;