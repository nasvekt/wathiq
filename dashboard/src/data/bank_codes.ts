export interface BankCode {
  code: string;
  name_en: string;
  name_ar: string;
}

export const BANK_CODES: BankCode[] = [
  { code: '10', name_en: 'National Commercial Bank', name_ar: 'البنك الأهلي التجاري' },
  { code: '20', name_en: 'Riyad Bank', name_ar: 'بنك الرياض' },
  { code: '30', name_en: 'Banque Saudi Fransi', name_ar: 'البنك السعودي الفرنسي' },
  { code: '40', name_en: 'Saudi British Bank (SABB)', name_ar: 'البنك السعودي البريطاني' },
  { code: '50', name_en: 'Al Rajhi Bank', name_ar: 'مصرف الراجحي' },
  { code: '60', name_en: 'Arab National Bank', name_ar: 'البنك العربي الوطني' },
  { code: '65', name_en: 'Saudi Investment Bank', name_ar: 'البنك السعودي للاستثمار' },
  { code: '70', name_en: 'Alinma Bank', name_ar: 'مصرف الإنماء' },
  { code: '80', name_en: 'Bank AlJazira', name_ar: 'بنك الجزيرة' },
  { code: '90', name_en: 'Alawwal Bank', name_ar: 'البنك الأول' },
  { code: '95', name_en: 'Gulf International Bank', name_ar: 'بنك الخليج الدولي' },
  { code: '99', name_en: 'Emirates NBD Saudi', name_ar: 'بنك الإمارات دبي الوطني' },
];

export function getBankName(code: string): string {
  const bank = BANK_CODES.find((b) => b.code === code);
  return bank?.name_en ?? `Bank ${code}`;
}

export function getBankNameArabic(code: string): string {
  const bank = BANK_CODES.find((b) => b.code === code);
  return bank?.name_ar ?? `بنك ${code}`;
}
