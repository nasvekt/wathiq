import { useQuery } from '@tanstack/react-query';
import { complianceApi } from '@/services/api';
import { useComplianceStore } from '@/store/compliance.store';

export function useDashboard() {
  const setDashboard = useComplianceStore((s) => s.setDashboard);

  return useQuery({
    queryKey: ['compliance', 'dashboard'],
    queryFn: async () => {
      const response = await complianceApi.getDashboard();
      setDashboard(response.data);
      return response.data;
    },
    staleTime: 30_000,
  });
}

export function useEmployees(params?: {
  search?: string;
  status?: string;
  nationality?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['compliance', 'employees', params],
    queryFn: async () => {
      const response = await complianceApi.getEmployees(params);
      return response.data;
    },
  });
}

export function useEmployee(id: string) {
  return useQuery({
    queryKey: ['compliance', 'employee', id],
    queryFn: async () => {
      const response = await complianceApi.getEmployee(id);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useHealthScore() {
  return useQuery({
    queryKey: ['compliance', 'health-score'],
    queryFn: async () => {
      const response = await complianceApi.getHealthScore();
      return response.data;
    },
    staleTime: 60_000,
  });
}

export function useIqamaCalendar() {
  return useQuery({
    queryKey: ['compliance', 'iqama-calendar'],
    queryFn: async () => {
      const response = await complianceApi.getIqamaCalendar();
      return response.data;
    },
  });
}

export function useContractTracker() {
  return useQuery({
    queryKey: ['compliance', 'contracts'],
    queryFn: async () => {
      const response = await complianceApi.getContractTracker();
      return response.data;
    },
  });
}

export function useComplianceTrends(range?: string) {
  return useQuery({
    queryKey: ['compliance', 'trends', range],
    queryFn: async () => {
      const response = await complianceApi.getComplianceTrends(range);
      return response.data;
    },
  });
}