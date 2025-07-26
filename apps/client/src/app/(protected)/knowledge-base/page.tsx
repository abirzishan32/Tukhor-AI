"use client";

import { useState, useEffect } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import {
    Database,
    RefreshCw,
    Trash2,
    Plus,
    FileText,
    BarChart3,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

interface KnowledgeBaseStatus {
    status: string;
    document_id?: string;
    chunk_count: number;
    total_words?: number;
    total_pages?: number;
}

interface VectorStoreStats {
    total_chunks: number;
    total_documents: number;
    language_distribution: Record<string, number>;
}

interface SystemStatus {
    system_ready: boolean;
    vector_store_stats: VectorStoreStats;
    embedding_model: string;
    chunk_settings: {
        chunk_size: number;
        chunk_overlap: number;
        top_k_chunks: number;
    };
}

export default function KnowledgeBasePage() {
    const [kbStatus, setKbStatus] = useState<KnowledgeBaseStatus | null>(null);
    const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isInitializing, setIsInitializing] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const fetchKnowledgeBaseStatus = async () => {
        try {
            const response = await api.get("/system/status");
            setSystemStatus(response.data);
        } catch (error) {
            console.error("Error fetching system status:", error);
            toast.error("Failed to fetch knowledge base status");
        }
    };

    const initializeKnowledgeBase = async () => {
        setIsInitializing(true);
        try {
            const response = await api.post("/system/initialize");
            setKbStatus(response.data.knowledge_base_status);
            await fetchKnowledgeBaseStatus();
            toast.success("Knowledge base initialized successfully");
        } catch (error: any) {
            console.error("Error initializing knowledge base:", error);
            toast.error(
                error.response?.data?.detail ||
                    "Failed to initialize knowledge base"
            );
        } finally {
            setIsInitializing(false);
        }
    };

    const deleteKnowledgeBase = async () => {
        if (
            !confirm(
                "Are you sure you want to delete the knowledge base? This action cannot be undone."
            )
        ) {
            return;
        }

        setIsDeleting(true);
        try {
            await api.delete("/system/knowledge-base");
            setKbStatus(null);
            await fetchKnowledgeBaseStatus();
            toast.success("Knowledge base deleted successfully");
        } catch (error: any) {
            console.error("Error deleting knowledge base:", error);
            toast.error(
                error.response?.data?.detail ||
                    "Failed to delete knowledge base"
            );
        } finally {
            setIsDeleting(false);
        }
    };

    const refreshStatus = async () => {
        setIsLoading(true);
        await fetchKnowledgeBaseStatus();
        setIsLoading(false);
    };

    useEffect(() => {
        const loadData = async () => {
            await fetchKnowledgeBaseStatus();
            setIsLoading(false);
        };
        loadData();
    }, []);

    const getStatusBadge = () => {
        if (!systemStatus) return null;

        if (
            systemStatus.system_ready &&
            systemStatus.vector_store_stats.total_chunks > 0
        ) {
            return (
                <Badge variant="default" className="bg-green-500">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Active
                </Badge>
            );
        } else if (systemStatus.vector_store_stats.total_documents > 0) {
            return (
                <Badge variant="secondary">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Partial
                </Badge>
            );
        } else {
            return (
                <Badge variant="destructive">
                    <XCircle className="w-3 h-3 mr-1" />
                    Not Initialized
                </Badge>
            );
        }
    };

    if (isLoading) {
        return (
            <div className="container mx-auto p-6 space-y-6">
                <div className="flex items-center justify-center min-h-[400px]">
                    <Loader2 className="w-8 h-8 animate-spin" />
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Knowledge Base Management
                    </h1>
                    <p className="text-muted-foreground">
                        Manage your RAG system's knowledge base and monitor its
                        status
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        onClick={refreshStatus}
                        disabled={isLoading}
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Status Overview */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <Database className="w-5 h-5" />
                                Knowledge Base Status
                            </CardTitle>
                            <CardDescription>
                                Current status and configuration of your
                                knowledge base
                            </CardDescription>
                        </div>
                        {getStatusBadge()}
                    </div>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* System Health */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Card>
                            <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-muted-foreground">
                                            Total Documents
                                        </p>
                                        <p className="text-2xl font-bold">
                                            {systemStatus?.vector_store_stats
                                                .total_documents || 0}
                                        </p>
                                    </div>
                                    <FileText className="w-8 h-8 text-muted-foreground" />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-muted-foreground">
                                            Total Chunks
                                        </p>
                                        <p className="text-2xl font-bold">
                                            {systemStatus?.vector_store_stats
                                                .total_chunks || 0}
                                        </p>
                                    </div>
                                    <BarChart3 className="w-8 h-8 text-muted-foreground" />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium text-muted-foreground">
                                            System Status
                                        </p>
                                        <p className="text-2xl font-bold">
                                            {systemStatus?.system_ready
                                                ? "Ready"
                                                : "Not Ready"}
                                        </p>
                                    </div>
                                    {systemStatus?.system_ready ? (
                                        <CheckCircle className="w-8 h-8 text-green-500" />
                                    ) : (
                                        <XCircle className="w-8 h-8 text-red-500" />
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <Separator />

                    {/* Configuration Details */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold">Configuration</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <p className="text-sm font-medium">
                                    Embedding Model
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    {systemStatus?.embedding_model}
                                </p>
                            </div>
                            <div className="space-y-2">
                                <p className="text-sm font-medium">
                                    Chunk Size
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    {systemStatus?.chunk_settings.chunk_size}{" "}
                                    characters
                                </p>
                            </div>
                            <div className="space-y-2">
                                <p className="text-sm font-medium">
                                    Chunk Overlap
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    {systemStatus?.chunk_settings.chunk_overlap}{" "}
                                    characters
                                </p>
                            </div>
                            <div className="space-y-2">
                                <p className="text-sm font-medium">
                                    Top-K Retrieval
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    {systemStatus?.chunk_settings.top_k_chunks}{" "}
                                    chunks
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Language Distribution */}
                    {systemStatus?.vector_store_stats.language_distribution && (
                        <>
                            <Separator />
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold">
                                    Language Distribution
                                </h3>
                                <div className="space-y-2">
                                    {Object.entries(
                                        systemStatus.vector_store_stats
                                            .language_distribution
                                    ).map(([lang, count]) => (
                                        <div
                                            key={lang}
                                            className="flex items-center justify-between"
                                        >
                                            <span className="text-sm font-medium capitalize">
                                                {lang === "bn"
                                                    ? "Bengali"
                                                    : lang === "en"
                                                    ? "English"
                                                    : lang}
                                            </span>
                                            <div className="flex items-center gap-2">
                                                <Progress
                                                    value={
                                                        (count /
                                                            systemStatus
                                                                .vector_store_stats
                                                                .total_documents) *
                                                        100
                                                    }
                                                    className="w-20"
                                                />
                                                <span className="text-sm text-muted-foreground">
                                                    {count}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>

            {/* Actions */}
            <Card>
                <CardHeader>
                    <CardTitle>Actions</CardTitle>
                    <CardDescription>
                        Initialize, update, or delete your knowledge base
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {!systemStatus?.system_ready ? (
                        <Alert>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                                Knowledge base is not ready. Please initialize
                                it to start using the RAG system.
                            </AlertDescription>
                        </Alert>
                    ) : (
                        <Alert>
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription>
                                Knowledge base is active and ready for queries.
                            </AlertDescription>
                        </Alert>
                    )}

                    <div className="flex flex-col sm:flex-row gap-3">
                        <Button
                            onClick={initializeKnowledgeBase}
                            disabled={isInitializing}
                            className="flex-1"
                        >
                            {isInitializing ? (
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                                <Plus className="w-4 h-4 mr-2" />
                            )}
                            {systemStatus?.system_ready
                                ? "Reinitialize"
                                : "Initialize"}{" "}
                            Knowledge Base
                        </Button>

                        {systemStatus?.system_ready && (
                            <Button
                                variant="destructive"
                                onClick={deleteKnowledgeBase}
                                disabled={isDeleting}
                                className="flex-1 sm:flex-initial"
                            >
                                {isDeleting ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <Trash2 className="w-4 h-4 mr-2" />
                                )}
                                Delete Knowledge Base
                            </Button>
                        )}
                    </div>

                    <div className="text-sm text-muted-foreground space-y-1">
                        <p>
                            <strong>Initialize:</strong> Downloads and processes
                            the HSC26 Bangla 1st Paper document into chunks.
                        </p>
                        <p>
                            <strong>Reinitialize:</strong> Replaces the existing
                            knowledge base with a fresh copy.
                        </p>
                        <p>
                            <strong>Delete:</strong> Permanently removes all
                            knowledge base data and chunks.
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
