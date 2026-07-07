import axios from 'axios';

// API base URL pointing to the FastAPI server
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface EpidemiologicalMetrics {
  total_cases: number;
  total_deaths: number;
  total_icu: number;
  total_vaccinated: number;
  mortality_rate: number;
  icu_rate: number;
  // Proportion of hospitalized SRAG cases with COVID vaccination (VACINA_COV=1).
  // NOT a population-level vaccination rate.
  hospitalized_vaccination_rate: number;
  case_increase_rate: number;
  cases_last_30_days?: number;
  cases_prev_30_days?: number;
}

export interface ChartData {
  daily_chart: Array<{ DT_NOTIFIC: string; case_count: number }>;
  monthly_chart: Array<{ month: string; case_count: number }>;
}

export interface NewsArticle {
  title: string;
  date: string;
  url: string;
  summary: string;
}

export interface ReportResponse {
  metrics: EpidemiologicalMetrics | null;
  charts: ChartData | null;
  explanation: string;
  news: NewsArticle[];
  execution_log: string[];
}

export interface ReportRequest {
  query: string;
  filters?: {
    start_date?: string;
    end_date?: string;
    uf?: string;
  };
}

export const fetchReport = async (payload: ReportRequest): Promise<ReportResponse> => {
  try {
    const { data } = await apiClient.post<ReportResponse>('/api/report', payload);
    return data;
  } catch (error: any) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error(error.message || 'An unexpected error occurred');
  }
};

export { API_BASE_URL };
