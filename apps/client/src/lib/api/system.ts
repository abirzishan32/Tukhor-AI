// System API functions
import axios from '@/lib/axios';

export interface SystemStatus {
    system_ready: boolean;
    vector_store_stats: {
        total_documents: number;
        total_chunks: number;
        total_vectors: number;
    };
    embedding_model: string;
    chunk_settings: {
        chunk_size: number;
        chunk_overlap: number;
        top_k_chunks: number;
    };
}

export interface HealthCheck {
    overall: string;
    database: string;
    vector_store: string;
    embedding_service: string;
    knowledge_base: string;
}

export interface InitializationResponse {
    message: string;
    knowledge_base_status: {
        status: string;
        document_id?: string;
        chunks_created?: number;
    };
    vector_store_stats: {
        total_documents: number;
        total_chunks: number;
        total_vectors: number;
    };
    system_ready: boolean;
}

export interface DeleteKnowledgeBaseResponse {
    message: string;
    status: string;
    document_id: string;
    chunks_deleted: number;
}

// System Operations
export async function getSystemStatus(): Promise<SystemStatus> {
    const response = await axios.get('/system/status');
    return response.data;
}

export async function getHealthCheck(): Promise<HealthCheck> {
    const response = await axios.get('/system/health');
    return response.data;
}

export async function initializeSystem(): Promise<InitializationResponse> {
    const response = await axios.post('/system/initialize');
    return response.data;
}

export async function deleteKnowledgeBase(): Promise<DeleteKnowledgeBaseResponse> {
    const response = await axios.delete('/system/knowledge-base');
    return response.data;
}

export default {
    getSystemStatus,
    getHealthCheck,
    initializeSystem,
    deleteKnowledgeBase,
};
