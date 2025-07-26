"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CodeBlock, InlineCode } from "./CodeBlock";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
    content: string;
    className?: string;
    isUser?: boolean;
}

export function MarkdownRenderer({ content, className, isUser = false }: MarkdownRendererProps) {
    return (
        <div className={cn("markdown-content", isUser && "user-message", className)}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}                components={{
                    // Code blocks
                    code: ({ className, children, ...props }: any) => {
                        const match = /language-(\w+)/.exec(className || "");
                        const language = match ? match[1] : undefined;
                        const isInline = !className?.includes("language-");
                        
                        if (isInline) {
                            return <InlineCode {...props}>{children}</InlineCode>;
                        }

                        return (
                            <CodeBlock
                                language={language}
                                value={String(children).replace(/\n$/, "")}
                                className={className}
                            />
                        );
                    },
                      // Links
                    a: ({ href, children }: any) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={cn(
                                "underline underline-offset-4 transition-colors",
                                isUser 
                                    ? "text-primary-foreground/80 hover:text-primary-foreground" 
                                    : "text-primary hover:text-primary/80"
                            )}
                        >
                            {children}
                        </a>
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
}
