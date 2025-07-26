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
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    BarChart3,
    MessageSquare,
    Target,
    Clock,
    TrendingUp,
    Search,
    Send,
    Loader2,
    ThumbsUp,
    ThumbsDown,
    Minus,
    RefreshCw,
    Download,
    Filter,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

interface EvaluationStats {
    total_queries: number;
    average_confidence: number;
    average_response_time: number;
    language_distribution: Record<string, number>;
    feedback_distribution: Record<string, number>;
    groundedness_scores: {
        average: number;
        distribution: Record<string, number>;
    };
    relevance_scores: {
        average: number;
        distribution: Record<string, number>;
    };
}

interface QueryResult {
    answer: string;
    sources: Array<{
        id: string;
        content: string;
        similarity: number;
        document_title: string;
        chunk_index: number;
    }>;
    confidence: number;
    response_time: number;
    language: string;
    chunks_retrieved: number;
    chat_id?: string;
}

interface TestQuery {
    question: string;
    expected_language: string;
    document_ids?: string[];
}

const testQueries: TestQuery[] = [
    {
        question: "শম্ভুনাথ কে?",
        expected_language: "bn",
    },
    {
        question: "Who is Shombhunath?",
        expected_language: "en",
    },
    {
        question: "বাংলা সাহিত্যে রবীন্দ্রনাথের অবদান কী?",
        expected_language: "bn",
    },
    {
        question: "What are the main themes in Bengali literature?",
        expected_language: "en",
    },
    {
        question: "HSC পরীক্ষার জন্য কি পড়তে হবে?",
        expected_language: "bn",
    },
];

export default function RAGEvaluationPage() {
    const [stats, setStats] = useState<EvaluationStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [currentQuery, setCurrentQuery] = useState("");
    const [isQuerying, setIsQuerying] = useState(false);
    const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
    const [selectedTestQuery, setSelectedTestQuery] = useState<string>("");
    const [isBatchTesting, setIsBatchTesting] = useState(false);
    const [batchResults, setBatchResults] = useState<
        Array<{ query: string; result: QueryResult; score: number }>
    >([]);

    const fetchEvaluationStats = async () => {
        try {
            const response = await api.get("/rag/evaluation/stats");
            setStats(response.data);
        } catch (error) {
            console.error("Error fetching evaluation stats:", error);
            toast.error("Failed to fetch evaluation statistics");
        }
    };

    const testSingleQuery = async (question: string) => {
        setIsQuerying(true);
        try {
            const response = await api.post("/rag/ask", {
                question,
                include_history: false,
            });
            setQueryResult(response.data);
            return response.data;
        } catch (error: any) {
            console.error("Error testing query:", error);
            toast.error(error.response?.data?.detail || "Failed to test query");
            return null;
        } finally {
            setIsQuerying(false);
        }
    };

    const runBatchTest = async () => {
        setIsBatchTesting(true);
        setBatchResults([]);

        try {
            const results = [];

            for (const testQuery of testQueries) {
                const result = await testSingleQuery(testQuery.question);
                if (result) {
                    // Calculate a simple evaluation score based on multiple factors
                    let score = 0;

                    // Language consistency (30%)
                    if (result.language === testQuery.expected_language) {
                        score += 30;
                    }

                    // Confidence score (40%)
                    score += result.confidence * 40;

                    // Response time score (20%) - better if under 5 seconds
                    const timeScore =
                        Math.max(0, (5 - result.response_time) / 5) * 20;
                    score += timeScore;

                    // Chunk retrieval score (10%) - better if more relevant chunks
                    const chunkScore =
                        Math.min(result.chunks_retrieved / 5, 1) * 10;
                    score += chunkScore;

                    results.push({
                        query: testQuery.question,
                        result,
                        score: Math.round(score),
                    });
                }

                // Add small delay between requests
                await new Promise((resolve) => setTimeout(resolve, 1000));
            }

            setBatchResults(results);
            toast.success(
                `Batch test completed: ${results.length} queries processed`
            );
        } catch (error) {
            toast.error("Batch test failed");
        } finally {
            setIsBatchTesting(false);
        }
    };

    const submitFeedback = async (
        messageId: string,
        feedback: "helpful" | "not_helpful" | "partial"
    ) => {
        try {
            await api.post("/rag/feedback", {
                message_id: messageId,
                feedback,
            });
            toast.success("Feedback submitted successfully");
        } catch (error) {
            toast.error("Failed to submit feedback");
        }
    };

    const refreshStats = async () => {
        setIsLoading(true);
        await fetchEvaluationStats();
        setIsLoading(false);
    };

    useEffect(() => {
        const loadData = async () => {
            await fetchEvaluationStats();
            setIsLoading(false);
        };
        loadData();
    }, []);

    const getScoreColor = (score: number) => {
        if (score >= 80) return "text-green-600";
        if (score >= 60) return "text-yellow-600";
        return "text-red-600";
    };

    const getScoreBadge = (score: number) => {
        if (score >= 80)
            return <Badge className="bg-green-500">Excellent</Badge>;
        if (score >= 60) return <Badge className="bg-yellow-500">Good</Badge>;
        return <Badge variant="destructive">Needs Improvement</Badge>;
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        RAG Evaluation
                    </h1>
                    <p className="text-muted-foreground">
                        Evaluate and test your RAG system's performance and
                        accuracy
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        onClick={refreshStats}
                        disabled={isLoading}
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            <Tabs defaultValue="overview" className="space-y-6">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="testing">Query Testing</TabsTrigger>
                    <TabsTrigger value="batch">Batch Evaluation</TabsTrigger>
                </TabsList>

                {/* Overview Tab */}
                <TabsContent value="overview" className="space-y-6">
                    {isLoading ? (
                        <div className="flex items-center justify-center min-h-[400px]">
                            <Loader2 className="w-8 h-8 animate-spin" />
                        </div>
                    ) : (
                        <>
                            {/* Key Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Total Queries
                                                </p>
                                                <p className="text-2xl font-bold">
                                                    {stats?.total_queries || 0}
                                                </p>
                                            </div>
                                            <MessageSquare className="w-8 h-8 text-muted-foreground" />
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Avg Confidence
                                                </p>
                                                <p className="text-2xl font-bold">
                                                    {(
                                                        (stats?.average_confidence ||
                                                            0) * 100
                                                    ).toFixed(1)}
                                                    %
                                                </p>
                                            </div>
                                            <Target className="w-8 h-8 text-muted-foreground" />
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Avg Response Time
                                                </p>
                                                <p className="text-2xl font-bold">
                                                    {(
                                                        stats?.average_response_time ||
                                                        0
                                                    ).toFixed(2)}
                                                    s
                                                </p>
                                            </div>
                                            <Clock className="w-8 h-8 text-muted-foreground" />
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Groundedness
                                                </p>
                                                <p className="text-2xl font-bold">
                                                    {(
                                                        (stats
                                                            ?.groundedness_scores
                                                            ?.average || 0) *
                                                        100
                                                    ).toFixed(1)}
                                                    %
                                                </p>
                                            </div>
                                            <TrendingUp className="w-8 h-8 text-muted-foreground" />
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Detailed Metrics */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Language Distribution */}
                                <Card>
                                    <CardHeader>
                                        <CardTitle>
                                            Language Distribution
                                        </CardTitle>
                                        <CardDescription>
                                            Query languages processed
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        {stats?.language_distribution &&
                                            Object.entries(
                                                stats.language_distribution
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
                                                                    stats.total_queries) *
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
                                    </CardContent>
                                </Card>

                                {/* User Feedback */}
                                <Card>
                                    <CardHeader>
                                        <CardTitle>User Feedback</CardTitle>
                                        <CardDescription>
                                            Quality ratings from users
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        {stats?.feedback_distribution &&
                                            Object.entries(
                                                stats.feedback_distribution
                                            ).map(([feedback, count]) => (
                                                <div
                                                    key={feedback}
                                                    className="flex items-center justify-between"
                                                >
                                                    <div className="flex items-center gap-2">
                                                        {feedback ===
                                                            "helpful" && (
                                                            <ThumbsUp className="w-4 h-4 text-green-500" />
                                                        )}
                                                        {feedback ===
                                                            "not_helpful" && (
                                                            <ThumbsDown className="w-4 h-4 text-red-500" />
                                                        )}
                                                        {feedback ===
                                                            "partial" && (
                                                            <Minus className="w-4 h-4 text-yellow-500" />
                                                        )}
                                                        <span className="text-sm font-medium capitalize">
                                                            {feedback.replace(
                                                                "_",
                                                                " "
                                                            )}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <Progress
                                                            value={
                                                                (count /
                                                                    Object.values(
                                                                        stats.feedback_distribution
                                                                    ).reduce(
                                                                        (
                                                                            a,
                                                                            b
                                                                        ) =>
                                                                            a +
                                                                            b,
                                                                        0
                                                                    )) *
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
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Relevance and Groundedness Scores */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Relevance Scores</CardTitle>
                                        <CardDescription>
                                            How relevant retrieved chunks are to
                                            queries
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-center mb-4">
                                            <div className="text-3xl font-bold">
                                                {(
                                                    (stats?.relevance_scores
                                                        ?.average || 0) * 100
                                                ).toFixed(1)}
                                                %
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                Average Relevance
                                            </div>
                                        </div>
                                        <Progress
                                            value={
                                                (stats?.relevance_scores
                                                    ?.average || 0) * 100
                                            }
                                            className="h-2"
                                        />
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle>
                                            Groundedness Scores
                                        </CardTitle>
                                        <CardDescription>
                                            How well answers are supported by
                                            sources
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-center mb-4">
                                            <div className="text-3xl font-bold">
                                                {(
                                                    (stats?.groundedness_scores
                                                        ?.average || 0) * 100
                                                ).toFixed(1)}
                                                %
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                Average Groundedness
                                            </div>
                                        </div>
                                        <Progress
                                            value={
                                                (stats?.groundedness_scores
                                                    ?.average || 0) * 100
                                            }
                                            className="h-2"
                                        />
                                    </CardContent>
                                </Card>
                            </div>
                        </>
                    )}
                </TabsContent>

                {/* Query Testing Tab */}
                <TabsContent value="testing" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Query Input */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Test Query</CardTitle>
                                <CardDescription>
                                    Enter a question to test the RAG system
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="test-query">Question</Label>
                                    <Textarea
                                        id="test-query"
                                        placeholder="Enter your question in Bengali or English..."
                                        value={currentQuery}
                                        onChange={(e) =>
                                            setCurrentQuery(e.target.value)
                                        }
                                        rows={3}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label>
                                        Or select a predefined test query
                                    </Label>
                                    <Select
                                        value={selectedTestQuery}
                                        onValueChange={(value) => {
                                            setSelectedTestQuery(value);
                                            setCurrentQuery(value);
                                        }}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Choose a test query..." />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {testQueries.map((query, index) => (
                                                <SelectItem
                                                    key={index}
                                                    value={query.question}
                                                >
                                                    {query.question}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <Button
                                    onClick={() =>
                                        testSingleQuery(currentQuery)
                                    }
                                    disabled={
                                        !currentQuery.trim() || isQuerying
                                    }
                                    className="w-full"
                                >
                                    {isQuerying ? (
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    ) : (
                                        <Send className="w-4 h-4 mr-2" />
                                    )}
                                    Test Query
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Query Results */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Query Results</CardTitle>
                                <CardDescription>
                                    Analysis of the RAG response
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                {queryResult ? (
                                    <div className="space-y-4">
                                        {/* Metrics */}
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Confidence
                                                </p>
                                                <p className="text-lg font-bold">
                                                    {(
                                                        queryResult.confidence *
                                                        100
                                                    ).toFixed(1)}
                                                    %
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Response Time
                                                </p>
                                                <p className="text-lg font-bold">
                                                    {queryResult.response_time.toFixed(
                                                        2
                                                    )}
                                                    s
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Language
                                                </p>
                                                <p className="text-lg font-bold capitalize">
                                                    {queryResult.language}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-muted-foreground">
                                                    Chunks Retrieved
                                                </p>
                                                <p className="text-lg font-bold">
                                                    {
                                                        queryResult.chunks_retrieved
                                                    }
                                                </p>
                                            </div>
                                        </div>

                                        <Separator />

                                        {/* Answer */}
                                        <div>
                                            <p className="text-sm font-medium text-muted-foreground mb-2">
                                                Answer
                                            </p>
                                            <p className="text-sm bg-muted p-3 rounded-md">
                                                {queryResult.answer}
                                            </p>
                                        </div>

                                        {/* Sources */}
                                        <div>
                                            <p className="text-sm font-medium text-muted-foreground mb-2">
                                                Sources (
                                                {queryResult.sources.length})
                                            </p>
                                            <div className="space-y-2 max-h-40 overflow-y-auto">
                                                {queryResult.sources.map(
                                                    (source, index) => (
                                                        <div
                                                            key={source.id}
                                                            className="text-xs bg-muted p-2 rounded-md"
                                                        >
                                                            <div className="flex justify-between items-center mb-1">
                                                                <span className="font-medium">
                                                                    Chunk{" "}
                                                                    {
                                                                        source.chunk_index
                                                                    }
                                                                </span>
                                                                <Badge variant="outline">
                                                                    {(
                                                                        source.similarity *
                                                                        100
                                                                    ).toFixed(
                                                                        1
                                                                    )}
                                                                    % similar
                                                                </Badge>
                                                            </div>
                                                            <p className="text-muted-foreground truncate">
                                                                {source.content}
                                                            </p>
                                                        </div>
                                                    )
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center h-40 text-muted-foreground">
                                        <div className="text-center">
                                            <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                            <p>
                                                Run a test query to see results
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Batch Evaluation Tab */}
                <TabsContent value="batch" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Batch Evaluation</CardTitle>
                            <CardDescription>
                                Run predefined test queries to evaluate overall
                                system performance
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Button
                                onClick={runBatchTest}
                                disabled={isBatchTesting}
                                className="w-full sm:w-auto"
                            >
                                {isBatchTesting ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <BarChart3 className="w-4 h-4 mr-2" />
                                )}
                                Run Batch Test ({testQueries.length} queries)
                            </Button>

                            {isBatchTesting && (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>Progress</span>
                                        <span>
                                            {batchResults.length} /{" "}
                                            {testQueries.length}
                                        </span>
                                    </div>
                                    <Progress
                                        value={
                                            (batchResults.length /
                                                testQueries.length) *
                                            100
                                        }
                                    />
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Batch Results */}
                    {batchResults.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Batch Test Results</CardTitle>
                                <CardDescription>
                                    Performance analysis of{" "}
                                    {batchResults.length} test queries
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {/* Summary */}
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">
                                                {(
                                                    batchResults.reduce(
                                                        (sum, r) =>
                                                            sum + r.score,
                                                        0
                                                    ) / batchResults.length
                                                ).toFixed(1)}
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                Average Score
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">
                                                {(
                                                    (batchResults.reduce(
                                                        (sum, r) =>
                                                            sum +
                                                            r.result.confidence,
                                                        0
                                                    ) /
                                                        batchResults.length) *
                                                    100
                                                ).toFixed(1)}
                                                %
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                Average Confidence
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">
                                                {(
                                                    batchResults.reduce(
                                                        (sum, r) =>
                                                            sum +
                                                            r.result
                                                                .response_time,
                                                        0
                                                    ) / batchResults.length
                                                ).toFixed(2)}
                                                s
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                Average Response Time
                                            </div>
                                        </div>
                                    </div>

                                    {/* Individual Results */}
                                    <div className="space-y-3">
                                        {batchResults.map((result, index) => (
                                            <div
                                                key={index}
                                                className="border rounded-lg p-4"
                                            >
                                                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
                                                    <div className="flex-1">
                                                        <p className="font-medium text-sm">
                                                            {result.query}
                                                        </p>
                                                        <p className="text-xs text-muted-foreground">
                                                            {
                                                                result.result
                                                                    .language
                                                            }{" "}
                                                            •{" "}
                                                            {result.result.response_time.toFixed(
                                                                2
                                                            )}
                                                            s •{" "}
                                                            {
                                                                result.result
                                                                    .chunks_retrieved
                                                            }{" "}
                                                            chunks
                                                        </p>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <div
                                                            className={`text-2xl font-bold ${getScoreColor(
                                                                result.score
                                                            )}`}
                                                        >
                                                            {result.score}
                                                        </div>
                                                        {getScoreBadge(
                                                            result.score
                                                        )}
                                                    </div>
                                                </div>
                                                <p className="text-sm bg-muted p-2 rounded truncate">
                                                    {result.result.answer}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
