import axiosBase, { AxiosInstance, AxiosResponse } from 'axios';
import { createClient } from '@/lib/supabase/client';

// Create the base Axios instance
const axios: AxiosInstance = axiosBase.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
axios.interceptors.request.use(
    async (config) => {
        const supabase = createClient();
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.access_token) {
            config.headers.Authorization = `Bearer ${session.access_token}`;
        }
        
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
axios.interceptors.response.use(
    (response: AxiosResponse) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                const supabase = createClient();
                const { data: { session }, error: refreshError } = await supabase.auth.refreshSession();
                
                if (refreshError || !session) {
                    return Promise.reject(error);
                }
                
                originalRequest.headers.Authorization = `Bearer ${session.access_token}`;
                return axios(originalRequest);
            } catch (refreshError) {
                console.error('Session refresh failed:', refreshError);
                return Promise.reject(error);
            }
        }
        
        return Promise.reject(error);
    }
);

export default axios;