import { create } from 'zustand';
import type { ComplianceDashboard, ComplianceFilter } from '@/types/compliance';

interface ComplianceState {
  dashboard: ComplianceDashboard | null;
  filter: ComplianceFilter;
  isLoading: boolean;
  error: string | null;
  setDashboard: (dashboard: ComplianceDashboard) => void;
  setFilter: (filter: Partial<ComplianceFilter>) => void;
  resetFilter: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const defaultFilter: ComplianceFilter = {
  search: '',
  status: '',
  nationality: '',
  nitaqat_weight: '',
  page: 1,
  page_size: 25,
};

export const useComplianceStore = create<ComplianceState>((set) => ({
  dashboard: null,
  filter: { ...defaultFilter },
  isLoading: false,
  error: null,
  setDashboard: (dashboard) => set({ dashboard, error: null }),
  setFilter: (filter) =>
    set((state) => ({ filter: { ...state.filter, ...filter } })),
  resetFilter: () => set({ filter: { ...defaultFilter } }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
