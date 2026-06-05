export interface SectorCode {
  code: string;
  name_en: string;
  name_ar: string;
  nitaqat_band_thresholds: {
    platinum: number;
    high_green: number;
    low_green: number;
    yellow: number;
  };
}

export const SECTOR_CODES: SectorCode[] = [
  {
    code: 'A',
    name_en: 'Agriculture, Forestry and Fishing',
    name_ar: 'الزراعة والحراجة وصيد الأسماك',
    nitaqat_band_thresholds: { platinum: 15, high_green: 10, low_green: 5, yellow: 2 },
  },
  {
    code: 'B',
    name_en: 'Mining and Quarrying',
    name_ar: 'التعدين والمحاجر',
    nitaqat_band_thresholds: { platinum: 20, high_green: 14, low_green: 8, yellow: 4 },
  },
  {
    code: 'C',
    name_en: 'Manufacturing',
    name_ar: 'الصناعة التحويلية',
    nitaqat_band_thresholds: { platinum: 18, high_green: 12, low_green: 6, yellow: 3 },
  },
  {
    code: 'F',
    name_en: 'Construction',
    name_ar: 'التشييد والبناء',
    nitaqat_band_thresholds: { platinum: 12, high_green: 8, low_green: 4, yellow: 2 },
  },
  {
    code: 'G',
    name_en: 'Wholesale and Retail Trade',
    name_ar: 'تجارة الجملة والتجزئة',
    nitaqat_band_thresholds: { platinum: 16, high_green: 11, low_green: 6, yellow: 3 },
  },
  {
    code: 'H',
    name_en: 'Transportation and Storage',
    name_ar: 'النقل والتخزين',
    nitaqat_band_thresholds: { platinum: 14, high_green: 9, low_green: 5, yellow: 2 },
  },
  {
    code: 'I',
    name_en: 'Accommodation and Food Services',
    name_ar: 'الإقامة والخدمات الغذائية',
    nitaqat_band_thresholds: { platinum: 20, high_green: 14, low_green: 8, yellow: 4 },
  },
  {
    code: 'J',
    name_en: 'Information and Communication',
    name_ar: 'المعلومات والاتصالات',
    nitaqat_band_thresholds: { platinum: 22, high_green: 15, low_green: 9, yellow: 5 },
  },
  {
    code: 'K',
    name_en: 'Financial and Insurance Activities',
    name_ar: 'الأنشطة المالية والتأمينية',
    nitaqat_band_thresholds: { platinum: 35, high_green: 25, low_green: 15, yellow: 8 },
  },
  {
    code: 'M',
    name_en: 'Professional, Scientific and Technical Activities',
    name_ar: 'الأنشطة المهنية والعلمية والتقنية',
    nitaqat_band_thresholds: { platinum: 20, high_green: 14, low_green: 8, yellow: 4 },
  },
  {
    code: 'N',
    name_en: 'Administrative and Support Services',
    name_ar: 'خدمات الإدارة والدعم',
    nitaqat_band_thresholds: { platinum: 15, high_green: 10, low_green: 5, yellow: 2 },
  },
  {
    code: 'Q',
    name_en: 'Human Health and Social Work',
    name_ar: 'الصحة البشرية والعمل الاجتماعي',
    nitaqat_band_thresholds: { platinum: 25, high_green: 18, low_green: 10, yellow: 5 },
  },
  {
    code: 'S',
    name_en: 'Other Service Activities',
    name_ar: 'أنشطة الخدمات الأخرى',
    nitaqat_band_thresholds: { platinum: 14, high_green: 9, low_green: 5, yellow: 2 },
  },
];

export function getSectorName(code: string): string {
  return SECTOR_CODES.find((s) => s.code === code)?.name_en ?? `Sector ${code}`;
}

export function getSectorNameArabic(code: string): string {
  return SECTOR_CODES.find((s) => s.code === code)?.name_ar ?? `قطاع ${code}`;
}
