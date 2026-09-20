import axios from 'axios';

// In development, use Vite proxy (/api) to avoid CORS issues.
// In production, use the direct API URL from env.
const isDev = import.meta.env.DEV;
const API_BASE_URL = isDev ? '/api' : (import.meta.env.VITE_API_BASE_URL || '');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.error ||
      error.message ||
      'An unexpected error occurred';
    console.error('[API Error]', message, error.response?.status, error.config?.url);
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
