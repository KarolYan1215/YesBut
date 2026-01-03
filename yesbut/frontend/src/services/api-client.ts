/**
 * API Client Service
 */

interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  withCredentials: boolean;
}

interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  private baseURL: string;
  private timeout: number;
  private withCredentials: boolean;

  constructor(config: ApiClientConfig) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout;
    this.withCredentials = config.withCredentials;
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, ...fetchOptions } = options;
    let url = `${this.baseURL}${endpoint}`;

    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: this.withCredentials ? 'include' : 'same-origin',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw transformError({ status: response.status, ...error });
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      throw transformError(error);
    }
  }

  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body: JSON.stringify(data) });
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body: JSON.stringify(data) });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export function createApiClient(config?: Partial<ApiClientConfig>): ApiClient {
  return new ApiClient({
    baseURL: process.env.NEXT_PUBLIC_API_URL || '/api/v1',
    timeout: 30000,
    withCredentials: true,
    ...config,
  });
}

export function transformError(error: unknown): ApiError {
  if (error && typeof error === 'object') {
    const err = error as Record<string, unknown>;
    return {
      code: String(err.code || err.status || 'UNKNOWN_ERROR'),
      message: String(err.message || 'An unexpected error occurred'),
      details: err.details as Record<string, unknown> | undefined,
    };
  }
  return { code: 'UNKNOWN_ERROR', message: 'An unexpected error occurred' };
}

export const apiClient = createApiClient();
export type { ApiClient, ApiError, ApiClientConfig };
