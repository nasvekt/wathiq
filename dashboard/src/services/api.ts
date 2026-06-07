import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach auth token + company_id
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('wathiq_token');
    const companyId = localStorage.getItem('wathiq_company_id');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (companyId) {
      config.headers['X-Company-ID'] = companyId;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('wathiq_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

// --- Auth ---
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: {
    email: string;
    password: string;
    company_name: string;
    industry: string;
    company_size: string;
  }) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
};

// --- Compliance ---
export const complianceApi = {
  getDashboard: () => api.get('/compliance/dashboard'),
  getEmployees: (params?: {
    search?: string;
    status?: string;
    nationality?: string;
    page?: number;
    page_size?: number;
  }) => api.get('/compliance/employees', { params }),
  getEmployee: (id: string) => api.get(`/compliance/employees/${id}`),
  getHealthScore: () => api.get('/compliance/health-score'),
  getIqamaCalendar: () => api.get('/compliance/iqama-calendar'),
  getContractTracker: () => api.get('/compliance/contracts'),
  getComplianceTrends: (range?: string) =>
    api.get('/compliance/trends', { params: { range } }),
};

// --- Nitaqat Simulator ---
export const simulatorApi = {
  simulate: (params: {
    current_expat_count: number;
    current_saudi_count: number;
    target_expat_count: number;
    target_saudi_count: number;
    industry: string;
    region: string;
    company_size: string;
  }) => api.post('/simulator/nitaqat', params),
};

// --- Wage Sync / SIF Export ---
export const wageSyncApi = {
  getBatches: () => api.get('/wage-sync/batches'),
  exportSif: (data: {
    batch_id: string;
    include_all: boolean;
    status_filter?: string;
  }) => api.post('/wage-sync/export', data, { responseType: 'blob' }),
};

// --- Developer ---
export const developerApi = {
  getApiKeys: () => api.get('/developer/keys'),
  createApiKey: (name: string) => api.post('/developer/keys', { name }),
  revokeApiKey: (id: string) => api.delete(`/developer/keys/${id}`),
};

// --- Billing ---
export const billingApi = {
  getInfo: () => api.get('/billing'),
  getInvoices: () => api.get('/billing/invoices'),
};

// --- Founder / Admin ---
export const founderApi = {
  getSummary: () => api.get('/founder/summary'),
  getUsers: () => api.get('/founder/users'),
};

export default api;
