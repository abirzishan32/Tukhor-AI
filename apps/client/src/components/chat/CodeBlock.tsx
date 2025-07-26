"use client";

import { useState, useEffect } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { Button } from "@/components/ui/button";
import { Copy, Check } from "lucide-react";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";

interface CodeBlockProps {
    language?: string;
    value: string;
    className?: string;
}

export function CodeBlock({ language, value, className }: CodeBlockProps) {
    const [copied, setCopied] = useState(false);
    const { theme } = useTheme();

    const copyToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(value);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error("Failed to copy code:", err);
        }
    };

    // Detect language from className if not provided
    const detectedLanguage = language || className?.replace("language-", "") || "text";
    
    // Use appropriate theme based on current theme
    const syntaxTheme = theme === "dark" ? oneDark : oneLight;

    return (
        <div className="relative group">
            {/* Header with language and copy button */}
            <div className="flex items-center justify-between px-4 py-2 bg-muted border-b border-border rounded-t-lg">
                <span className="text-xs font-medium text-muted-foreground uppercase">
                    {detectedLanguage}
                </span>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={copyToClipboard}
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                    {copied ? (
                        <Check className="h-3 w-3 text-green-500" />
                    ) : (
                        <Copy className="h-3 w-3" />
                    )}
                </Button>
            </div>

            {/* Code content */}
            <div className="relative overflow-x-auto">
                <SyntaxHighlighter
                    language={detectedLanguage}
                    style={syntaxTheme}
                    customStyle={{
                        margin: 0,
                        borderRadius: "0 0 8px 8px",
                        background: theme === "dark" ? "#1e1e1e" : "#f8f8f8",
                        fontSize: "0.875rem",
                        lineHeight: "1.5",
                    }}
                    showLineNumbers={value.split("\n").length > 3}
                    wrapLines={true}
                    wrapLongLines={true}
                >
                    {value}
                </SyntaxHighlighter>
            </div>
        </div>
    );
}

// Inline code component
export function InlineCode({ children, className }: { children: React.ReactNode; className?: string }) {
    return (
        <code className={cn(
            "relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold",
            className
        )}>
            {children}
        </code>
    );
}
