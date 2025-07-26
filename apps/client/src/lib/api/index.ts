// Main API index - exports all API functions
export * from './chat';
export * from './documents';
export * from './system';

// Re-export default objects for convenience
export { default as chatApi } from './chat';
export { default as documentsApi } from './documents';
export { default as systemApi } from './system';

// Create a unified API client for pages that need direct axios-like interface
import axios from '@/lib/axios';

export const api = {
    get: axios.get,
    post: axios.post,
    put: axios.put,
    delete: axios.delete,
    patch: axios.patch,
};
