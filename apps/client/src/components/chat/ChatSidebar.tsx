"use client";

import { useState, useEffect, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import {
    Plus,
    Search,
    MessageSquare,
    Trash2,
    MoreVertical,
    Menu,
    X,
    Loader2,
} from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, formatRelativeDate } from "@/lib/utils";
import { Chat, getUserChats, deleteChat } from "@/lib/api/chat";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

interface ChatSidebarProps {
    currentChatId?: string;
    onChatSelect: (chatId: string) => void;
    onNewChat: () => void;
    className?: string;
    isMobile?: boolean;
}

export function ChatSidebar({
    currentChatId,
    onChatSelect,
    onNewChat,
    className,
    isMobile = false,
}: ChatSidebarProps) {
    const [chats, setChats] = useState<Chat[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [hasMore, setHasMore] = useState(false);
    const [pagination, setPagination] = useState({
        limit: 20,
        offset: 0,
        total: 0
    });
    const router = useRouter();    const loadChats = async (reset = false) => {
        try {
            if (reset) {
                setLoading(true);
                setChats([]);
                setPagination(prev => ({ ...prev, offset: 0 }));
            } else {
                setLoadingMore(true);
            }

            const currentOffset = reset ? 0 : pagination.offset;
            const { chats: chatList, pagination: paginationData } = await getUserChats(
                pagination.limit, 
                currentOffset
            );
            
            if (reset) {
                setChats(chatList);
            } else {
                setChats(prev => [...prev, ...chatList]);
            }
            
            setPagination(prev => ({
                ...prev,
                offset: currentOffset + chatList.length,
                total: paginationData.total
            }));
            
            setHasMore(paginationData.hasMore);
        } catch (error) {
            console.error("Error loading chats:", error);
            toast.error("Failed to load chats");
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    };

    const loadMoreChats = () => {
        if (!loadingMore && hasMore) {
            loadChats(false);
        }
    };    useEffect(() => {
        loadChats(true);
    }, []);

    const filteredChats = useMemo(() => {
        if (!searchQuery.trim()) return chats;
        return chats.filter(
            (chat) =>
                chat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                chat.lastMessage
                    ?.toLowerCase()
                    .includes(searchQuery.toLowerCase())
        );
    }, [chats, searchQuery]);
    const handleNewChat = async () => {
        try {
            // Navigate to dashboard for new chat - chat will be created when first message is sent
            onNewChat();
            if (isMobile) setIsOpen(false);
        } catch (error) {
            console.error("Error creating chat:", error);
            toast.error("Failed to create new chat");
        }
    };
    const handleDeleteChat = async (chatId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            await deleteChat(chatId);
            setChats((prev) => prev.filter((chat) => chat.id !== chatId));
            if (currentChatId === chatId) {
                // Redirect to dashboard if current chat is deleted
                router.push("/dashboard");
            }
        } catch (error) {
            console.error("Error deleting chat:", error);
            toast.error("Failed to delete chat");
        }
    };

    const SidebarContent = () => (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Chats</h2>
                    {isMobile && (
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setIsOpen(false)}
                        >
                            <X className="h-4 w-4" />
                        </Button>
                    )}
                </div>

                <Button
                    onClick={handleNewChat}
                    className="w-full justify-start gap-2"
                    variant="outline"
                >
                    <Plus className="h-4 w-4" />
                    New Chat
                </Button>
            </div>

            {/* Search */}
            <div className="p-4 border-b">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search chats..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9"
                    />
                </div>
            </div>

            {/* Chat List */}
            <ScrollArea className="flex-1">
                <div className="p-2">
                    {loading ? (
                        <div className="space-y-2">
                            {Array.from({ length: 5 }).map((_, i) => (
                                <div
                                    key={i}
                                    className="p-3 rounded-lg bg-muted animate-pulse"
                                >
                                    <div className="h-4 bg-muted-foreground/20 rounded w-3/4 mb-2" />
                                    <div className="h-3 bg-muted-foreground/20 rounded w-1/2" />
                                </div>
                            ))}
                        </div>
                    ) : filteredChats.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            {searchQuery ? "No chats found" : "No chats yet"}
                        </div>
                    ) : (                        <div className="space-y-1">
                            {filteredChats.map((chat) => (
                                <div
                                    key={chat.id}
                                    className={cn(
                                        "group relative p-3 rounded-lg cursor-pointer transition-colors hover:bg-accent",
                                        currentChatId === chat.id && "bg-accent"
                                    )}
                                    onClick={() => {
                                        onChatSelect(chat.id);
                                        if (isMobile) setIsOpen(false);
                                    }}
                                >
                                    {/* ...existing chat item content... */}
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                                                <h3 className="text-sm font-medium truncate">
                                                    {chat.name}
                                                </h3>
                                            </div>

                                            {chat.lastMessage && (
                                                <p className="text-xs text-muted-foreground truncate">
                                                    {chat.lastMessage}
                                                </p>
                                            )}

                                            <div className="flex items-center justify-between mt-2">
                                                <span className="text-xs text-muted-foreground">
                                                    {formatRelativeDate(
                                                        chat.updated_at ||
                                                            chat.created_at
                                                    )}
                                                </span>
                                                <span className="text-xs text-muted-foreground">
                                                    {chat.messageCount} messages
                                                </span>
                                            </div>
                                        </div>

                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                                                    onClick={(e) =>
                                                        e.stopPropagation()
                                                    }
                                                >
                                                    <MoreVertical className="h-3 w-3" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem
                                                    onClick={(e) =>
                                                        handleDeleteChat(
                                                            chat.id,
                                                            e
                                                        )
                                                    }
                                                    className="text-destructive focus:text-destructive"
                                                >
                                                    <Trash2 className="h-4 w-4 mr-2" />
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </div>
                                </div>
                            ))}
                            
                            {/* Load More Button */}
                            {!searchQuery && hasMore && (
                                <div className="p-2">
                                    <Button
                                        variant="outline"
                                        onClick={loadMoreChats}
                                        disabled={loadingMore}
                                        className="w-full"
                                    >
                                        {loadingMore ? (
                                            <>
                                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                Loading...
                                            </>
                                        ) : (
                                            `Load More (${pagination.total - chats.length} remaining)`
                                        )}
                                    </Button>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </ScrollArea>
        </div>
    );

    if (isMobile) {
        return (
            <Sheet open={isOpen} onOpenChange={setIsOpen}>
                <SheetTrigger asChild>
                    <Button variant="ghost" size="icon" className="md:hidden">
                        <Menu className="h-5 w-5" />
                    </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-80 p-0">
                    <SidebarContent />
                </SheetContent>
            </Sheet>
        );
    }

    return (
        <div className={cn("w-80 border-r bg-muted/10", className)}>
            <SidebarContent />
        </div>
    );
}
