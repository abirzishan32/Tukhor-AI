'use client';
import { Button } from "@/components/ui/button";
import axios from "@/lib/axios";
import { useState } from "react";

export default function TestPage() {
    const [response, setResponse] = useState<any>(null);
    const testSession = async () => {
        try {
            const data = await axios.get("/api/v1/test/models");
            setResponse(data.data);
        } catch (error:any) {
            console.error("Error testing session:", error);
            setResponse({
                error: "Failed to fetch data",
                details: error.message,
            });
        }
    }

    return (
        <div className="flex flex-col items-center justify-center h-full">
            <h1 className="text-2xl font-bold mb-4">Test Page</h1>
            <p className="text-gray-600">This is a protected test page.</p>
            <Button onClick={testSession}>Test server auth</Button>
            <span>Test Auth</span>
            {response && (
                <div className="mt-4 p-4 rounded">
                    <h2 className="text-lg font-semibold">Response:</h2>
                    <pre className="p-2 rounded">{JSON.stringify(response, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}