import Link from "next/link";
import { AuthButton } from "@/components/auth/auth-button";
import { ThemeSwitcher } from "@/components/global/theme-switcher";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    BookOpen,
    MessageSquare,
    Search,
    FileText,
    Brain,
    Languages,
    CheckCircle,
    Sparkles,
    ArrowRight,
    Upload,
    Users,
    Database,
} from "lucide-react";

export default function Home() {
    return (
        <main className="min-h-screen flex flex-col">
            <nav className="w-full flex justify-center border-b border-b-foreground/10 h-16 sticky top-0 bg-background/80 backdrop-blur-md z-50">
                <div className="w-full max-w-7xl flex justify-between items-center p-3 px-5 text-sm">
                    <div className="flex gap-5 items-center font-semibold text-2xl">
                        <Link href={"/"} className="flex items-center gap-2">
                            <BookOpen className="h-8 w-8 text-primary" />
                            তুখোড়
                        </Link>
                    </div>
                    <AuthButton dashboard />
                </div>
            </nav>

            {/* Hero Section */}
            <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-br from-primary/5 via-background to-secondary/5">
                <div className="container px-4 md:px-6 max-w-7xl mx-auto">
                    <div className="flex flex-col items-center space-y-4 text-center">
                        <div className="space-y-2">
                            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                                বাংলা সাহিত্যের জন্য
                                <span className="text-primary block mt-2">
                                    AI-Powered Assistant
                                </span>
                            </h1>
                            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl leading-relaxed">
                                তুখোড় হলো একটি উন্নত RAG সিস্টেম যা বাংলা ও
                                ইংরেজি ভাষায় সাহিত্য বিষয়ক প্রশ্নের নির্ভুল
                                উত্তর প্রদান করে। HSC পাঠ্যক্রম থেকে শুরু করে
                                বিস্তৃত সাহিত্য জ্ঞান - সবই এক জায়গায়।
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-4 mt-8">
                            <Button asChild size="lg" className="text-lg px-8">
                                <Link href="/dashboard">
                                    <MessageSquare className="mr-2 h-5 w-5" />
                                    Start Chatting
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <Button
                                variant="outline"
                                size="lg"
                                className="text-lg px-8"
                            >
                                <FileText className="mr-2 h-5 w-5" />
                                View Documentation
                            </Button>
                        </div>
                        <div className="flex flex-wrap justify-center gap-2 mt-6">
                            <Badge variant="secondary" className="px-3 py-1">
                                <Languages className="mr-1 h-3 w-3" />
                                বাংলা + English
                            </Badge>
                            <Badge variant="secondary" className="px-3 py-1">
                                <Brain className="mr-1 h-3 w-3" />
                                AI-Powered
                            </Badge>
                            <Badge variant="secondary" className="px-3 py-1">
                                <BookOpen className="mr-1 h-3 w-3" />
                                HSC Ready
                            </Badge>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="w-full py-12 md:py-24 lg:py-32">
                <div className="container px-4 md:px-6 max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
                            Powerful Features
                        </h2>
                        <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                            উন্নত প্রযুক্তি ও ব্যবহারকারী-বান্ধব ইন্টারফেসের
                            সমন্বয়ে তৈরি
                        </p>
                    </div>

                    <div className="grid gap-6 lg:grid-cols-3 md:grid-cols-2">
                        <Card className="border-2 hover:border-primary/50 transition-colors">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <Languages className="h-8 w-8 text-primary" />
                                    <CardTitle>Bilingual Support</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="text-base">
                                    বাংলা ও ইংরেজি উভয় ভাষায় প্রশ্ন করুন এবং
                                    প্রাসঙ্গিক উত্তর পান। ভাষা পরিবর্তন করার
                                    প্রয়োজন নেই।
                                </CardDescription>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 transition-colors">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <Search className="h-8 w-8 text-primary" />
                                    <CardTitle>Smart Search</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="text-base">
                                    Vector-based similarity search যা semantic
                                    meaning বুঝতে পারে এবং সবচেয়ে প্রাসঙ্গিক
                                    তথ্য খুঁজে দেয়।
                                </CardDescription>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 transition-colors">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <MessageSquare className="h-8 w-8 text-primary" />
                                    <CardTitle>Conversation Memory</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="text-base">
                                    আগের কথোপকথন মনে রাখে এবং context অনুযায়ী
                                    আরও ভালো ও সঠিক উত্তর প্রদান করে।
                                </CardDescription>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 transition-colors">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <Upload className="h-8 w-8 text-primary" />
                                    <CardTitle>Document Upload</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="text-base">
                                    নতুন PDF ডকুমেন্ট আপলোড করুন এবং তা থেকে
                                    তাৎক্ষণিক প্রশ্ন-উত্তর সুবিধা পান।
                                </CardDescription>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 transition-colors">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <Database className="h-8 w-8 text-primary" />
                                    <CardTitle>Source Attribution</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="text-base">
                                    প্রতিটি উত্তরের সাথে সোর্স রেফারেন্স এবং
                                    নির্ভরযোগ্যতার স্কোর পান।
                                </CardDescription>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 transition-colors">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <Users className="h-8 w-8 text-primary" />
                                    <CardTitle>Multi-Session</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <CardDescription className="text-base">
                                    একাধিক chat session চালু রাখুন এবং বিভিন্ন
                                    টপিক নিয়ে আলাদা আলাদা আলোচনা করুন।
                                </CardDescription>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </section>

            {/* Use Cases Section */}
            <section className="w-full py-12 md:py-24 lg:py-32 bg-muted/50">
                <div className="container px-4 md:px-6 max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
                            Who Can Use তুখোড়?
                        </h2>
                        <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                            শিক্ষার্থী থেকে গবেষক - সবার জন্য উপযোগী
                        </p>
                    </div>

                    <div className="grid gap-8 lg:grid-cols-2">
                        <Card className="p-6">
                            <CardHeader className="pb-4">
                                <CardTitle className="flex items-center gap-2 text-xl">
                                    <BookOpen className="h-6 w-6 text-primary" />
                                    HSC Students
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="flex items-start gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                                    <span>
                                        বাংলা প্রথম পত্রের সমস্ত টপিক কভার
                                    </span>
                                </div>
                                <div className="flex items-start gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                                    <span>
                                        পরীক্ষার প্রস্তুতিতে সহায়ক প্রশ্ন-উত্তর
                                    </span>
                                </div>
                                <div className="flex items-start gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                                    <span>তাৎক্ষণিক সন্দেহ নিরসন</span>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="p-6">
                            <CardHeader className="pb-4">
                                <CardTitle className="flex items-center gap-2 text-xl">
                                    <Sparkles className="h-6 w-6 text-primary" />
                                    Researchers & Teachers
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="flex items-start gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                                    <span>দ্রুত তথ্য অনুসন্ধান ও যাচাইকরণ</span>
                                </div>
                                <div className="flex items-start gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                                    <span>গবেষণার জন্য রেফারেন্স খোঁজা</span>
                                </div>
                                <div className="flex items-start gap-2">
                                    <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                                    <span>ক্লাস প্রস্তুতিতে সহায়তা</span>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="w-full py-12 md:py-24 lg:py-32">
                <div className="container px-4 md:px-6 max-w-7xl mx-auto">
                    <div className="flex flex-col items-center space-y-4 text-center">
                        <div className="space-y-2">
                            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                                Ready to Get Started?
                            </h2>
                            <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl">
                                আজই শুরু করুন এবং বাংলা সাহিত্যের জগতে AI-এর
                                শক্তি অনুভব করুন
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-4 mt-8">
                            <Button asChild size="lg" className="text-lg px-8">
                                <Link href="/dashboard">
                                    <MessageSquare className="mr-2 h-5 w-5" />
                                    Start Your First Chat
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

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
