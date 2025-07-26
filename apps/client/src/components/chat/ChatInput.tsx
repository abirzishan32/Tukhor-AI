"use client";

import { useState, useRef, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Square, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
    onSendMessage: (message: string) => Promise<void>;
    isLoading?: boolean;
    disabled?: boolean;
    placeholder?: string;
    className?: string;
}

export function ChatInput({
    onSendMessage,
    isLoading = false,
    disabled = false,
    placeholder = "Ask a question in Bengali or English...",
    className,
}: ChatInputProps) {
    const [message, setMessage] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = async () => {
        if (!message.trim() || isSubmitting || disabled) return;

        const messageToSend = message.trim();
        setMessage("");
        setIsSubmitting(true);

        try {
            await onSendMessage(messageToSend);
        } catch (error) {
            // Restore message on error
            setMessage(messageToSend);
            console.error("Error sending message:", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const adjustTextareaHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = "auto";
            textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
        }
    };

    const currentlyLoading = isLoading || isSubmitting;

    return (
        <div
            className={cn(
                "relative flex items-end gap-2 p-4 border-t bg-background",
                className
            )}
        >
            <div className="flex-1 relative">
                <Textarea
                    ref={textareaRef}
                    value={message}
                    onChange={(e) => {
                        setMessage(e.target.value);
                        adjustTextareaHeight();
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    disabled={disabled || currentlyLoading}
                    className="min-h-[44px] max-h-[120px] resize-none pr-12 text-sm"
                    rows={1}
                />

                {/* Character count indicator */}
                {message.length > 800 && (
                    <div className="absolute bottom-2 right-14 text-xs text-muted-foreground">
                        {message.length}/1000
                    </div>
                )}
            </div>

            <Button
                onClick={handleSubmit}
                disabled={!message.trim() || disabled || currentlyLoading}
                size="icon"
                className="h-11 w-11 shrink-0"
            >
                {currentlyLoading ? (
                    <Square className="h-4 w-4" />
                ) : (
                    <Send className="h-4 w-4" />
                )}
            </Button>
        </div>
    );
}
