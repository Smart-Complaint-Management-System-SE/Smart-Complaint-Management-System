export type UserRole = 'user' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export type ComplaintStatus = 'Pending' | 'In Progress' | 'Resolved';

export interface ComplaintUpdate {
  id: number;
  old_status: string;
  new_status: string;
  note: string;
  created_at: string;
}

export interface Complaint {
  id: number;
  title: string;
  description: string;
  category: string;
  status: ComplaintStatus;
  resolution?: string | null;
  created_at: string;
  updated_at?: string | null;
  user_id?: number;
  user_name?: string;
  user_email?: string;
}

export interface ComplaintDetail extends Complaint {
  history: ComplaintUpdate[];
}

export interface Category {
  id: number;
  name: string;
  created_at?: string;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ComplaintsResponse extends PaginationMeta {
  complaints: Complaint[];
}

export interface UserStats {
  Pending: number;
  'In Progress': number;
  Resolved: number;
  total: number;
}

export interface AdminStats {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
  categories: { name: string; count: number }[];
  recent_activity: {
    id: number;
    title: string;
    status: string;
    updated_at: string;
    user_name: string;
  }[];
}
