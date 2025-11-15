export interface Department {
  id: number;
  name: string;
  code: string;
  created_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  department: number;
  department_name: string;
  role: 'doctor' | 'admin';
}

export interface Patient {
  id: number;
  hospital_id: string;
  name: string;
  age: number;
  gender: 'M' | 'F' | 'O';
  bed_ward_info?: string;
  created_at: string;
  updated_at: string;
}

export interface ConsultComment {
  id: number;
  consult: number;
  author: number;
  author_name: string;
  author_username: string;
  message: string;
  created_at: string;
}

export interface ConsultRequest {
  id: number;
  patient: number;
  patient_details: Patient;
  from_department: number;
  from_department_name: string;
  to_department: number;
  to_department_name: string;
  requested_by: number;
  requested_by_name: string;
  priority: 'routine' | 'urgent' | 'stat';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  clinical_summary: string;
  consult_question: string;
  created_at: string;
  updated_at: string;
  comments: ConsultComment[];
  comment_count: number;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
