import axios from 'axios';

const API = '/api/v1';

export const qiwaApi = {
  upload: (data: {
    company_name?: string;
    employees: any[];
  }) => axios.post(`${API}/qiwa/upload`, data),

  getStatus: (scanId: string) =>
    axios.get(`${API}/qiwa/status/${scanId}`),

  simulate: (data: {
    scan_id: string;
    add_saudi: number;
    add_saudi_documented?: boolean;
    increase_salaries_for?: string[];
  }) => axios.post(`${API}/qiwa/simulate`, data),

  generateReport: (data: {
    scan_id: string;
    company_name?: string;
  }) => axios.post(`${API}/qiwa/report`, data),
};