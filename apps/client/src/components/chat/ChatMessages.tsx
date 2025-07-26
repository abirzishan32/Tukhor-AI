"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
    User,
    Bot,
    Copy,
    ThumbsUp,
    ThumbsDown,
    MoreHorizontal,
    ExternalLink,
    FileText,
    MessageSquare,
    Loader2,
} from "lucide-react";
import { MarkdownRenderer } from "./MarkdownRenderer";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn, formatMessageTime } from "@/lib/utils";
import { Message, submitFeedback, getChatHistory } from "@/lib/api/chat";
import { toast } from "sonner";

interface ChatMessagesProps {
    messages: Message[];
    isLoading?: boolean;
    className?: string;
    chatId?: string; // Add chatId for pagination
    onLoadMoreMessages?: (olderMessages: Message[]) => void; // Callback for loading more messages
}

interface MessageItemProps {
    message: Message;
    isLatest?: boolean;
}

function MessageItem({ message, isLatest }: MessageItemProps) {
    const [feedbackGiven, setFeedbackGiven] = useState(false);
    const [showSources, setShowSources] = useState(false);

    const handleFeedback = async (feedback: "helpful" | "not_helpful") => {
        try {
            await submitFeedback(message.id, feedback);
            setFeedbackGiven(true);
        } catch (error) {
            console.error("Error submitting feedback:", error);
        }
    };    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard");
    };

    const isUser = message.role === "user";
    const hasRetrievedChunks =
        message.retrievedChunks && message.retrievedChunks.length > 0;

    return (
        <div
            className={cn(
                "flex gap-3 p-4",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            {!isUser && (
                <div className="shrink-0">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-primary" />
                    </div>
                </div>
            )}

            <div
                className={cn("max-w-[80%] space-y-2", isUser && "order-first")}
            >                {/* Message Content */}
                <div
                    className={cn(
                        "rounded-lg px-4 py-3 text-sm",
                        isUser
                            ? "bg-primary text-primary-foreground ml-auto"
                            : "bg-muted"
                    )}
                >
                    <MarkdownRenderer 
                        content={message.content} 
                        isUser={isUser}
                    />
                </div>

                {/* Message Metadata */}
                <div
                    className={cn(
                        "flex items-center gap-2 text-xs text-muted-foreground",
                        isUser && "justify-end"
                    )}
                >
                    {" "}
                    <span>{formatMessageTime(message.createdAt)}</span>
                    {!isUser && message.groundingScore && (
                        <Badge variant="outline" className="text-xs">
                            Confidence:{" "}
                            {Math.round(message.groundingScore * 100)}%
                        </Badge>
                    )}
                </div>

                {/* AI Message Actions */}
                {!isUser && (
                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(message.content)}
                            className="h-7 px-2 text-xs"
                        >
                            <Copy className="w-3 h-3 mr-1" />
                            Copy
                        </Button>

                        {hasRetrievedChunks && (
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowSources(!showSources)}
                                className="h-7 px-2 text-xs"
                            >
                                <FileText className="w-3 h-3 mr-1" />
                                Sources ({message.retrievedChunks!.length})
                            </Button>
                        )}

                        {/* Feedback Buttons */}
                        {!feedbackGiven && (
                            <div className="flex gap-1">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleFeedback("helpful")}
                                    className="h-7 w-7 p-0"
                                >
                                    <ThumbsUp className="w-3 h-3" />
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() =>
                                        handleFeedback("not_helpful")
                                    }
                                    className="h-7 w-7 p-0"
                                >
                                    <ThumbsDown className="w-3 h-3" />
                                </Button>
                            </div>
                        )}

                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-7 w-7 p-0"
                                >
                                    <MoreHorizontal className="w-3 h-3" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="start">
                                <DropdownMenuItem
                                    onClick={() =>
                                        copyToClipboard(message.content)
                                    }
                                >
                                    <Copy className="w-4 h-4 mr-2" />
                                    Copy message
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                )}

                {/* Sources */}
                {hasRetrievedChunks && (
                    <Collapsible
                        open={showSources}
                        onOpenChange={setShowSources}
                    >
                        <CollapsibleContent className="space-y-2">
                            <div className="text-xs font-medium text-muted-foreground">
                                Sources used:
                            </div>
                            {message.retrievedChunks!.map(
                                (chunk: any, index: number) => (
                                    <Card key={index} className="bg-muted/50">
                                        <CardContent className="p-3">
                                            <div className="flex items-start justify-between gap-2 mb-2">
                                                <div className="text-xs font-medium text-muted-foreground">
                                                    {chunk.document_title ||
                                                        "Unknown Document"}
                                                </div>
                                                <Badge
                                                    variant="outline"
                                                    className="text-xs"
                                                >
                                                    {Math.round(
                                                        chunk.similarity * 100
                                                    )}
                                                    % match
                                                </Badge>
                                            </div>
                                            <p className="text-xs text-muted-foreground line-clamp-3">
                                                {chunk.content}
                                            </p>
                                        </CardContent>
                                    </Card>
                                )
                            )}
                        </CollapsibleContent>
                    </Collapsible>
                )}
            </div>

            {isUser && (
                <div className="shrink-0">
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                        <User className="w-4 h-4 text-muted-foreground" />
                    </div>
                </div>
            )}
        </div>
    );
}

export function ChatMessages({
    messages,
    isLoading,
    className,
    chatId,
    onLoadMoreMessages
}: ChatMessagesProps) {
    const scrollAreaRef = useRef<HTMLDivElement>(null);
    const bottomRef = useRef<HTMLDivElement>(null);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMoreMessages, setHasMoreMessages] = useState(true);
    const [currentOffset, setCurrentOffset] = useState(0);

    // Scroll to bottom when new messages are added (not when loading older messages)
    useEffect(() => {
        if (!isLoadingMore) {
            bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isLoadingMore]);

    // Handle scroll to top for infinite scroll
    const handleScroll = useCallback(async (event: React.UIEvent<HTMLDivElement>) => {
        const target = event.currentTarget;
        
        // Check if user scrolled to the top (with small threshold)
        if (target.scrollTop <= 100 && hasMoreMessages && !isLoadingMore && chatId && onLoadMoreMessages) {
            setIsLoadingMore(true);
            
            try {
                const { messages: olderMessages, pagination } = await getChatHistory(
                    chatId, 
                    20, // limit
                    currentOffset + messages.length // offset
                );
                
                if (olderMessages.length > 0) {
                    onLoadMoreMessages(olderMessages);
                    setCurrentOffset(prev => prev + olderMessages.length);
                }
                
                setHasMoreMessages(pagination.hasMore);
            } catch (error) {
                console.error("Error loading more messages:", error);
                toast.error("Failed to load more messages");
            } finally {
                setIsLoadingMore(false);
            }
        }
    }, [hasMoreMessages, isLoadingMore, chatId, onLoadMoreMessages, currentOffset, messages.length]);    return (
        <ScrollArea 
            className={cn("h-full", className)}
            ref={scrollAreaRef}
            onScrollCapture={handleScroll}
        >
            <div className="space-y-0 p-4">
                {/* Loading indicator for older messages */}
                {isLoadingMore && (
                    <div className="flex justify-center py-4">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Loading older messages...
                        </div>
                    </div>
                )}

                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
                        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                            <MessageSquare className="w-8 h-8 text-primary" />
                        </div>
                        <h3 className="text-lg font-semibold mb-2">
                            Start a conversation
                        </h3>
                        <p className="text-muted-foreground max-w-md">
                            Ask questions about Bengali literature, HSC
                            curriculum, or any topic. I can help in both Bengali
                            and English.
                        </p>
                    </div>
                ) : (
                    <>
                        {messages.map((message, index) => (
                            <MessageItem
                                key={message.id}
                                message={message}
                                isLatest={index === messages.length - 1}
                            />
                        ))}

                        {isLoading && (
                            <div className="flex gap-3 p-4">
                                <div className="shrink-0">
                                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-primary" />
                                    </div>
                                </div>
                                <div className="bg-muted rounded-lg px-4 py-3 text-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="flex space-x-1">
                                            <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:0ms]"></div>
                                            <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:100ms]"></div>
                                            <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:200ms]"></div>
                                        </div>
                                        <span className="text-muted-foreground">
                                            Thinking...
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                )}
                <div ref={bottomRef} />
            </div>
        </ScrollArea>
    );
}
