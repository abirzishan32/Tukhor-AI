"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatMessages } from "@/components/chat/ChatMessages";
import { ChatInput } from "@/components/chat/ChatInput";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Settings,
    MoreVertical,
    Trash2,
    Download,
    Share,
    Sidebar,
} from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, formatRelativeDate } from "@/lib/utils";
import {
    Message,
    Chat,
    getChatDetails,
    sendMessage,
    deleteChat,
} from "@/lib/api/chat";
import { toast } from "sonner";

interface ChatPageProps {
    chatId?: string;
    className?: string;
}

export function ChatPage({ chatId, className }: ChatPageProps) {
    const [currentChat, setCurrentChat] = useState<Chat | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const router = useRouter();    const loadChatData = async (id: string) => {
        try {
            setIsLoading(true);
            const chatData = await getChatDetails(id, 50, 0); // Load first 50 messages
            setCurrentChat(chatData.chat);
            setMessages(chatData.messages);
        } catch (error) {
            console.error("Error loading chat:", error);
            toast.error("Failed to load chat");
        } finally {
            setIsLoading(false);
        }
    };

    const handleLoadMoreMessages = (olderMessages: Message[]) => {
        // Prepend older messages to the current messages
        setMessages(prev => [...olderMessages, ...prev]);
    };

    useEffect(() => {
        if (chatId) {
            loadChatData(chatId);
        } else {
            setCurrentChat(null);
            setMessages([]);
        }
    }, [chatId]);

    const handleSendMessage = async (messageContent: string) => {
        if (!messageContent.trim()) return;

        // Add user message to UI immediately
        const userMessage: Message = {
            id: `temp-${Date.now()}`,
            content: messageContent,
            role: "user",
            createdAt: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            const response = await sendMessage(messageContent, chatId);

            // Remove temp user message and add real messages
            setMessages((prev) => {
                const filtered = prev.filter(
                    (msg) => msg.id !== userMessage.id
                );
                return [
                    ...filtered,
                    {
                        id: `user-${response.messageId}`,
                        content: messageContent,
                        role: "user" as const,
                        createdAt: new Date().toISOString(),
                    },
                    {
                        id: response.messageId,
                        content: response.answer,
                        role: "ai" as const,
                        createdAt: new Date().toISOString(),
                        groundingScore: response.groundingScore,
                        retrievedChunks: response.sources,
                    },
                ];
            });

            // Update current chat if this is a new chat
            if (!chatId && response.chatId) {
                router.push(`/dashboard/chat/${response.chatId}`);
            }
        } catch (error) {
            console.error("Error sending message:", error); // Remove the temp user message on error
            setMessages((prev) =>
                prev.filter((msg) => msg.id !== userMessage.id)
            );
            toast.error("Failed to send message");
        } finally {
            setIsLoading(false);
        }
    };

    const handleChatSelect = (selectedChatId: string) => {
        router.push(`/dashboard/chat/${selectedChatId}`);
    };

    const handleNewChat = () => {
        router.push("/dashboard");
    };

    const handleDeleteCurrentChat = async () => {
        if (!currentChat) return;
        try {
            await deleteChat(currentChat.id);
            toast.success("Chat deleted successfully");
            router.push("/dashboard");
        } catch (error) {
            console.error("Error deleting chat:", error);
            toast.error("Failed to delete chat");
        }
    };

    const exportChat = () => {
        if (!currentChat || !messages.length) return;

        const chatContent = messages
            .map((msg) => `${msg.role.toUpperCase()}: ${msg.content}`)
            .join("\n\n");

        const blob = new Blob([chatContent], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${currentChat.name.replace(/[^a-z0-9]/gi, "_")}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };
    return (
        <div className={cn("flex w-full h-full bg-background", className)}>
            {/* Sidebar */}
            <ChatSidebar
                currentChatId={chatId}
                onChatSelect={handleChatSelect}
                onNewChat={handleNewChat}
                isMobile={false}
                className={cn(
                    "transition-all duration-300 h-full",
                    isSidebarOpen ? "w-80" : "w-0 overflow-hidden"
                )}
            />

            {/* Mobile Sidebar */}
            <div className="md:hidden">
                <ChatSidebar
                    currentChatId={chatId}
                    onChatSelect={handleChatSelect}
                    onNewChat={handleNewChat}
                    isMobile={true}
                />
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col h-full min-h-0">
                {/* Chat Header */}
                {currentChat && (
                    <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex-shrink-0">
                        <div className="flex items-center justify-between p-4">
                            <div className="flex items-center gap-3">
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() =>
                                        setIsSidebarOpen(!isSidebarOpen)
                                    }
                                    className="hidden md:flex"
                                >
                                    <Sidebar className="h-4 w-4" />
                                </Button>

                                <div>
                                    <h1 className="text-lg font-semibold">
                                        {currentChat.name}
                                    </h1>
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <span>{messages.length} messages</span>{" "}
                                        <Badge
                                            variant="outline"
                                            className="text-xs"
                                        >
                                            {currentChat.updated_at
                                                ? formatRelativeDate(
                                                      currentChat.updated_at
                                                  )
                                                : "New"}
                                        </Badge>
                                    </div>
                                </div>
                            </div>

                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon">
                                        <MoreVertical className="h-4 w-4" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                    <DropdownMenuItem onClick={exportChat}>
                                        <Download className="h-4 w-4 mr-2" />
                                        Export chat
                                    </DropdownMenuItem>
                                    <DropdownMenuItem>
                                        <Share className="h-4 w-4 mr-2" />
                                        Share
                                    </DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem
                                        onClick={handleDeleteCurrentChat}
                                        className="text-destructive focus:text-destructive"
                                    >
                                        <Trash2 className="h-4 w-4 mr-2" />
                                        Delete chat
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </div>
                    </div>
                )}                {/* Messages Area */}
                <ChatMessages
                    messages={messages}
                    isLoading={isLoading}
                    className="flex-1 min-h-0"
                    chatId={chatId}
                    onLoadMoreMessages={handleLoadMoreMessages}
                />

                {/* Input Area */}
                <ChatInput
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                    placeholder={
                        currentChat
                            ? "Continue the conversation..."
                            : "Start a new conversation..."
                    }
                    className="flex-shrink-0"
                />
            </div>
        </div>
    );
}
