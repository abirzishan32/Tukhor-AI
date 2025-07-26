// Documents API functions
import axios from '@/lib/axios';

export interface Document {
    document_id: string;
    filename: string;
    language: string;
    chunk_count: number;
    word_count: number;
    page_count: number;
    file_url: string;
    created_at?: string;
    updated_at?: string;
}

export interface DocumentStats {
    total_documents: number;
    total_chunks: number;
    total_words: number;
    total_pages: number;
    languages: Record<string, number>;
}

export interface BatchUploadResult {
    successful_uploads: number;
    failed_uploads: number;
    results: Array<{
        filename: string;
        document_id: string;
        language: string;
        chunk_count: number;
        status: string;
    }>;
    errors: Array<{
        filename: string;
        error: string;
    }>;
}

// Document Management
export async function uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post('/documents/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
}

export async function getUserDocuments(): Promise<{
    documents: Document[];
    total_count: number;
}> {
    const response = await axios.get('/documents/');
    return response.data;
}

export async function getDocumentDetails(documentId: string): Promise<Document> {
    const response = await axios.get(`/documents/${documentId}`);
    return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
    await axios.delete(`/documents/${documentId}`);
}

export async function getDocumentStats(): Promise<DocumentStats> {
    const response = await axios.get('/documents/stats/overview');
    return response.data;
}

export async function batchUploadDocuments(files: File[]): Promise<BatchUploadResult> {
    const formData = new FormData();

    files.forEach((file) => {
        formData.append('files', file);
    });

    const response = await axios.post('/documents/batch-upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
}

export async function initializeKnowledgeBase(): Promise<{
    message: string;
    result: any;
}> {
    const response = await axios.post('/documents/initialize-kb');
    return response.data;
}

export default {
    uploadDocument,
    getUserDocuments,
    getDocumentDetails,
    deleteDocument,
    getDocumentStats,
    batchUploadDocuments,
    initializeKnowledgeBase,
};
