import React, { useState, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import * as XLSX from 'xlsx';

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
  const [parsedCount, setParsedCount] = useState(0);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const COLUMN_MAP: Record<string, string> = {
    'employee_name': 'employee_name',
    'name': 'employee_name',
    'full name': 'employee_name',
    'الاسم': 'employee_name',
    'iqama_number': 'iqama_number',
    'iqama': 'iqama_number',
    'iqama id': 'iqama_number',
    'id number': 'iqama_number',
    'رقم الإقامة': 'iqama_number',
    'basic_salary': 'basic_salary',
    'basic salary': 'basic_salary',
    'salary': 'basic_salary',
    'الراتب الأساسي': 'basic_salary',
    'contract_documented_in_qiwa': 'contract_documented_in_qiwa',
    'qiwa documented': 'contract_documented_in_qiwa',
    'qiwa': 'contract_documented_in_qiwa',
    'documented': 'contract_documented_in_qiwa',
    'موثق في قوى': 'contract_documented_in_qiwa',
    'gosi_enrolled': 'gosi_enrolled',
    'gosi': 'gosi_enrolled',
    'مسجل في التأمينات': 'gosi_enrolled',
    'nationality': 'nationality',
    'الجنسية': 'nationality',
    'job_title': 'job_title',
    'job title': 'job_title',
    'title': 'job_title',
    'المسمى الوظيفي': 'job_title',
    'total_gross_wage': 'total_gross_wage',
    'total gross': 'total_gross_wage',
    'gross salary': 'total_gross_wage',
    'إجمالي الراتب': 'total_gross_wage',
    'monthly_hours': 'monthly_hours',
    'hours': 'monthly_hours',
    'work hours': 'monthly_hours',
    'ساعات العمل': 'monthly_hours',
  };

  const parseFile = (data: ArrayBuffer) => {
    const workbook = XLSX.read(data, { type: 'array' });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const json = XLSX.utils.sheet_to_json(sheet, { defval: '' }) as Record<string, any>[];

    if (json.length === 0) {
      alert('No data found in the file.');
      return;
    }

    // Auto-detect columns
    const headers = Object.keys(json[0]);
    const mappedFields = headers.map(h => {
      const key = h.toLowerCase().trim().replace(/[^a-z0-9_\u0621-\u064A\s]/g, '');
      return COLUMN_MAP[key] || null;
    });

    const parsed = json.map((row: Record<string, any>, i: number) => {
      const emp: any = {
        ref_id: `emp-${(i + 1).toString().padStart(3, '0')}`,
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

      headers.forEach((h, idx) => {
        const field = mappedFields[idx];
        if (!field) return;
        const val = row[h];
        if (field === 'employee_name') emp.employee_name = String(val || '');
        else if (field === 'iqama_number') emp.iqama_number = String(val || '');
        else if (field === 'basic_salary' || field === 'total_gross_wage') {
          const num = Number(val) || 0;
          emp[field] = Math.max(num, 0);
        }
        else if (field === 'contract_documented_in_qiwa') emp.contract_documented_in_qiwa = String(val).toLowerCase() === 'yes' || val === true;
        else if (field === 'gosi_enrolled') emp.gosi_enrolled = String(val).toLowerCase() === 'yes' || val === true;
        else if (field === 'nationality') {
          emp.nationality = String(val || 'Saudi Arabia');
          emp.is_saudi = String(val).toLowerCase().includes('saudi');
        }
        else if (field === 'job_title') emp.job_title = String(val || '');
        else if (field === 'monthly_hours') emp.monthly_hours = Number(val) || 0;
      });

      // Auto-compute total gross
      if (emp.total_gross_wage < emp.basic_salary) {
        emp.total_gross_wage = emp.basic_salary;
      }

      return emp;
    });

    setEmployees(parsed);
    setParsedCount(parsed.length);
    setFileName(fileName || 'Uploaded file');
  };

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (ev) => {
        if (ev.target?.result) parseFile(ev.target.result as ArrayBuffer);
      };
      reader.readAsArrayBuffer(file);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (ev) => {
        if (ev.target?.result) parseFile(ev.target.result as ArrayBuffer);
      };
      reader.readAsArrayBuffer(file);
    }
  };

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

  const handleSubmit = () => {
    if (!employees.length) return;
    onSubmit(employees, companyName);
  };

  if (mode === 'excel') {
    return (
      <div>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".xlsx,.xls,.csv"
          className="hidden"
        />
        {parsedCount === 0 ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleFileDrop}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition mb-6 ${
              dragOver ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-gray-400 bg-white'
            }`}
          >
            <svg className="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-gray-600 font-medium mb-1">{t('qiwaShield.dragDrop')}</p>
            <p className="text-sm text-gray-400">{t('qiwaShield.supportedFormats')}</p>
          </div>
        ) : (
          <div>
            <div className="bg-green-50 border border-green-200 rounded-2xl p-5 text-center mb-6">
              <p className="text-green-800 font-medium">{parsedCount} {t('qiwaShield.totalEmployees')} {t('qiwaShield.scanning')}</p>
              <button onClick={() => { setParsedCount(0); setEmployees([]); }} className="text-sm text-primary hover:text-primary-dark mt-1 transition">
                Upload different file
              </button>
            </div>

            {/* Company Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('qiwaShield.companyName')}</label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-primary outline-none"
                placeholder={t('qiwaShield.companyNamePlaceholder')}
              />
            </div>

            {/* Parsed data preview */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-4">
              <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
                <p className="text-sm font-medium text-gray-700">{parsedCount} employees — preview</p>
              </div>
              <div className="overflow-x-auto max-h-64 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-gray-50">
                    <tr>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.name')}</th>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">IQAMA</th>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.salary')}</th>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">{t('qiwaShield.qiwaDoc')}</th>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500 uppercase">GOSI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.slice(0, 50).map((emp, i) => (
                      <tr key={i} className="border-t border-gray-100">
                        <td className="px-3 py-2 text-gray-900">{emp.employee_name}</td>
                        <td className="px-3 py-2 text-gray-500">{emp.iqama_number}</td>
                        <td className="px-3 py-2 text-gray-900">SAR {emp.basic_salary?.toLocaleString()}</td>
                        <td className="px-3 py-2">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            emp.contract_documented_in_qiwa ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                          }`}>
                            {emp.contract_documented_in_qiwa ? '✅' : '❌'}
                          </span>
                        </td>
                        <td className="px-3 py-2">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            emp.gosi_enrolled ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                          }`}>
                            {emp.gosi_enrolled ? '✅' : '❌'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {employees.length > 50 && (
                <div className="px-4 py-2 bg-gray-50 text-center text-xs text-gray-500">
                  Showing 50 of {employees.length} employees
                </div>
              )}
            </div>
          </div>
        )}
        <div className="flex items-center gap-3 mt-4">
          <button onClick={onBack} className="px-5 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
            {t('common.back')}
          </button>
          {parsedCount > 0 && (
            <button
              onClick={handleSubmit}
              disabled={!employees.some(e => e.employee_name)}
              className="px-6 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary-dark rounded-lg transition disabled:opacity-50"
            >
              {t('qiwaShield.scanEmployees')} ({parsedCount})
            </button>
          )}
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