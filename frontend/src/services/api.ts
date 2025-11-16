import axios from 'axios';
import type {
  Department,
  Patient,
  ConsultRequest,
  ConsultComment,
  LoginResponse,
  PaginatedResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login/`, {
      username,
      password,
    });
    return response.data;
  },
};

// Departments API
export const departmentsAPI = {
  list: async (): Promise<Department[]> => {
    const response = await api.get<Department[]>('/api/departments/');
    return response.data;
  },
};

// Patients API
export const patientsAPI = {
  list: async (search?: string): Promise<PaginatedResponse<Patient>> => {
    const response = await api.get<PaginatedResponse<Patient>>('/api/patients/', {
      params: { search },
    });
    return response.data;
  },
  create: async (patient: Omit<Patient, 'id' | 'created_at' | 'updated_at'>): Promise<Patient> => {
    const response = await api.post<Patient>('/api/patients/', patient);
    return response.data;
  },
  get: async (id: number): Promise<Patient> => {
    const response = await api.get<Patient>(`/api/patients/${id}/`);
    return response.data;
  },
};

// Consults API
export const consultsAPI = {
  list: async (params?: {
    role?: 'incoming' | 'outgoing';
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<ConsultRequest>> => {
    const response = await api.get<PaginatedResponse<ConsultRequest>>('/api/consults/', {
      params,
    });
    return response.data;
  },
  
  create: async (data: {
    patient?: number;
    patient_data?: Omit<Patient, 'id' | 'created_at' | 'updated_at'>;
    to_department: number;
    priority: string;
    clinical_summary: string;
    consult_question: string;
  }): Promise<ConsultRequest> => {
    const response = await api.post<ConsultRequest>('/api/consults/', data);
    return response.data;
  },
  
  get: async (id: number): Promise<ConsultRequest> => {
    const response = await api.get<ConsultRequest>(`/api/consults/${id}/`);
    return response.data;
  },
  
  updateStatus: async (id: number, status: string): Promise<ConsultRequest> => {
    const response = await api.patch<ConsultRequest>(`/api/consults/${id}/update_status/`, {
      status,
    });
    return response.data;
  },
  
  addComment: async (id: number, message: string): Promise<ConsultComment> => {
    const response = await api.post<ConsultComment>(`/api/consults/${id}/add_comment/`, {
      message,
    });
    return response.data;
  },
  
  getComments: async (id: number): Promise<ConsultComment[]> => {
    const response = await api.get<ConsultComment[]>(`/api/consults/${id}/comments/`);
    return response.data;
  },
};

export default api;
