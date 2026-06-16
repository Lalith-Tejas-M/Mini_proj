import axios from 'axios';
import { toast } from 'react-hot-toast';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Backend URL
  timeout: 120000, // 2 mins for heavy extraction/whisper tasks
});

// Interceptor for simple error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    toast.error(message);
    return Promise.reject(error);
  }
);

export default api;
