import {
  User,
  Complaint,
  ComplaintDetail,
  ComplaintsResponse,
  Category,
  UserStats,
  AdminStats,
  ComplaintStatus,
} from '../types';

let cachedCsrfToken: string | null = null;

export async function getCsrfToken(forceRefresh = false): Promise<string> {
  if (cachedCsrfToken && !forceRefresh) return cachedCsrfToken;

  try {
    const res = await fetch('/api/csrf-token', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      cachedCsrfToken = data.csrf_token || null;
      return cachedCsrfToken || '';
    }
  } catch (err) {
    console.warn('Could not fetch CSRF token from /api/csrf-token:', err);
  }

  return '';
}

export function setCsrfToken(token: string | null) {
  cachedCsrfToken = token;
}

export function clearCsrfToken() {
  cachedCsrfToken = null;
}

export async function request<T>(
  url: string,
  options: RequestInit & { _isRetry?: boolean } = {}
): Promise<T> {
  const method = (options.method || 'GET').toUpperCase();
  const headers = new Headers(options.headers || {});

  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }

  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const csrf = await getCsrfToken();
    if (csrf && !headers.has('X-CSRF-Token')) {
      headers.set('X-CSRF-Token', csrf);
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (response.status === 204) {
    return {} as T;
  }

  // Automatic retry once on 400 for mutating calls if CSRF was stale
  if (response.status === 400 && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && !options._isRetry) {
    clearCsrfToken();
    const freshCsrf = await getCsrfToken(true);
    const retryHeaders = new Headers(options.headers || {});
    if (!retryHeaders.has('Accept')) retryHeaders.set('Accept', 'application/json');
    if (!retryHeaders.has('Content-Type') && !(options.body instanceof FormData)) {
      retryHeaders.set('Content-Type', 'application/json');
    }
    if (freshCsrf) {
      retryHeaders.set('X-CSRF-Token', freshCsrf);
    }
    return request<T>(url, {
      ...options,
      headers: retryHeaders,
      _isRetry: true,
    });
  }

  const contentType = response.headers.get('content-type') || '';
  let data: any = null;

  if (contentType.includes('application/json')) {
    data = await response.json();
  } else {
    const text = await response.text();
    try {
      data = JSON.parse(text);
    } catch {
      data = { message: text };
    }
  }

  if (!response.ok) {
    let errorMessage = data?.error || data?.message;
    if (typeof errorMessage !== 'string') {
      errorMessage = '';
    }
    const lower = errorMessage.toLowerCase();
    if (
      !errorMessage ||
      lower.includes('<!doctype') ||
      lower.includes('<html') ||
      lower.includes('<body') ||
      /<[a-z][\s\S]*>/i.test(errorMessage)
    ) {
      if (response.status === 400) {
        errorMessage = 'Session or security token expired. Please try submitting again.';
      } else if (response.status === 401) {
        errorMessage = 'Your session has expired. Please sign in again.';
      } else if (response.status === 403) {
        errorMessage = 'Access denied. You do not have permission for this action.';
      } else if (response.status === 404) {
        errorMessage = 'The requested resource was not found.';
      } else if (response.status >= 500) {
        errorMessage = 'Internal server error. Please try again shortly.';
      } else {
        errorMessage = `Request failed with status ${response.status}`;
      }
    }
    const error = new Error(errorMessage);
    (error as any).status = response.status;
    (error as any).data = data;
    throw error;
  }

  return data as T;
}

export const authApi = {
  async getMe(): Promise<{ authenticated: boolean; user: User | null }> {
    return request('/api/auth/me');
  },

  async login(email: string, password: string): Promise<{ success: boolean; user: User; csrf_token?: string }> {
    clearCsrfToken();
    const result = await request<{ success: boolean; user: User; csrf_token?: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (result.csrf_token) {
      setCsrfToken(result.csrf_token);
    } else {
      await getCsrfToken(true);
    }
    return result;
  },

  async register(name: string, email: string, password: string): Promise<{ success: boolean; message: string }> {
    return request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  async logout(): Promise<{ success: boolean }> {
    try {
      const res = await request<{ success: boolean; csrf_token?: string }>('/api/auth/logout', {
        method: 'POST',
      });
      if (res.csrf_token) {
        setCsrfToken(res.csrf_token);
      } else {
        clearCsrfToken();
      }
      return res;
    } catch {
      clearCsrfToken();
      return { success: true };
    }
  },
};

export const complaintsApi = {
  async list(page = 1, perPage = 10, status?: string, category?: string, search?: string): Promise<ComplaintsResponse> {
    const params = new URLSearchParams({
      page: String(page),
      per_page: String(perPage),
      format: 'json',
    });
    if (status) params.set('status', status);
    if (category) params.set('category', category);
    if (search) params.set('search', search);

    return request(`/complaints?${params.toString()}`);
  },

  async get(id: number): Promise<ComplaintDetail> {
    return request(`/complaints/${id}?format=json`);
  },

  async create(title: string, description: string, category: string): Promise<{ success: boolean; complaint: Complaint }> {
    return request('/api/complaints', {
      method: 'POST',
      body: JSON.stringify({ title, description, category }),
    });
  },

  async getUserStats(): Promise<UserStats> {
    return request('/api/user/stats');
  },
};

export const adminApi = {
  async listComplaints(params: {
    page?: number;
    per_page?: number;
    status?: string;
    category?: string;
    sort?: string;
    search?: string;
  } = {}): Promise<ComplaintsResponse> {
    const sp = new URLSearchParams({ format: 'json' });
    if (params.page) sp.set('page', String(params.page));
    if (params.per_page) sp.set('per_page', String(params.per_page));
    if (params.status) sp.set('status', params.status);
    if (params.category) sp.set('category', params.category);
    if (params.sort) sp.set('sort', params.sort);
    if (params.search) sp.set('search', params.search);

    return request(`/api/admin/complaints?${sp.toString()}`);
  },

  async getStats(): Promise<AdminStats> {
    return request('/api/admin/stats');
  },

  async updateStatus(
    complaintId: number,
    payload: { status: ComplaintStatus; resolution?: string; reason?: string }
  ): Promise<{ success: boolean; complaint: Complaint }> {
    return request(`/complaints/${complaintId}/status`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },
};

export const categoriesApi = {
  async listAvailable(): Promise<Category[]> {
    return request('/api/complaint-categories');
  },

  async listAdmin(): Promise<Category[]> {
    return request('/api/categories');
  },

  async create(name: string): Promise<Category> {
    return request('/api/categories', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  },

  async update(id: number, name: string): Promise<Category> {
    return request(`/api/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    });
  },

  async delete(id: number): Promise<{ message: string }> {
    return request(`/api/categories/${id}`, {
      method: 'DELETE',
    });
  },
};
