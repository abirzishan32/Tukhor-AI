import { AuthButton } from "@/components/auth/auth-button";
import { ThemeSwitcher } from "@/components/global/theme-switcher";
import Link from "next/link";
import { BookOpen } from "lucide-react";

export default function ProtectedLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <main className="h-screen flex flex-col overflow-hidden">
            {/* Navigation */}
            <nav className="w-full border-b border-b-foreground/10 h-16 flex-shrink-0">
                <div className="w-full max-w-7xl mx-auto flex justify-between items-center p-3 px-5 text-sm h-full">
                    <div className="flex gap-5 items-center">
                        <Link
                            href={"/dashboard"}
                            className="font-semibold text-2xl"
                        >
                            তুখোড়
                        </Link>
                        <div className="flex gap-4 ml-8">
                            <Link
                                href="/dashboard"
                                className="text-sm font-medium hover:text-primary transition-colors"
                            >
                                Chat
                            </Link>
                            <Link
                                href="/knowledge-base"
                                className="text-sm font-medium hover:text-primary transition-colors"
                            >
                                Knowledge Base
                            </Link>
                            <Link
                                href="/evaluation"
                                className="text-sm font-medium hover:text-primary transition-colors"
                            >
                                Evaluation
                            </Link>
                        </div>
                    </div>
                    <div className="flex gap-5 items-center">
                        <ThemeSwitcher />
                        <AuthButton />
                    </div>
                </div>
            </nav>

            {/* Main Content Area */}
            <div className="flex-1 w-full overflow-y-auto">{children}</div>

            {/* Footer */}
            <footer className="w-full border-t">
                <div className="container px-4 md:px-6 max-w-7xl mx-auto">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4 py-8">
                        <div className="flex items-center gap-2">
                            <BookOpen className="h-5 w-5 text-primary" />
                            <span className="font-semibold">তুখোড়</span>
                            <span className="text-muted-foreground">
                                - Bengali Literature AI Assistant
                            </span>
                        </div>
                        <div className="flex items-center gap-6 text-sm text-muted-foreground">
                            <span>
                                Powered by{" "}
                                <Link
                                    href="https://supabase.com"
                                    target="_blank"
                                    className="font-bold hover:underline"
                                    rel="noreferrer"
                                >
                                    Supabase
                                </Link>
                            </span>
                            <ThemeSwitcher />
                        </div>
                    </div>
                </div>
            </footer>
        </main>
    );
}
