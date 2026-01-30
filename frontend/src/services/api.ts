const BASE_URL = "http://localhost:3020/api";

export interface ChatRequest {
    message: string;
    session_id: string;
}

export interface ChatResponse {
    message: string;
    tool_results?: ToolResult[];
    session_id: string;
}

export interface ToolResult {
    result?: {
        result?: {
            code: string;
            message: string;
            data: unknown;
        };
    };
    error?: string;
}

export interface Tool {
    name: string;
    description: string;
    input_schema: Record<string, unknown>;
}

export interface HealthResponse {
    status: string;
    message: string;
}

class ApiService {
    async healthCheck(): Promise<HealthResponse> {
        const response = await fetch(`${BASE_URL}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.statusText}`);
        }
        return response.json();
    }

    async chat(request: ChatRequest): Promise<ChatResponse> {
        const response = await fetch(`${BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            throw new Error(`Chat request failed: ${response.statusText}`);
        }

        return response.json();
    }

    async getSessions(): Promise<string[]> {
        const response = await fetch(`${BASE_URL}/sessions`);
        if (!response.ok) {
            throw new Error(`Failed to get sessions: ${response.statusText}`);
        }
        return response.json();
    }

    async clearSession(sessionId: string): Promise<{ message: string }> {
        const response = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error(`Failed to clear session: ${response.statusText}`);
        }
        return response.json();
    }
}

export const apiService = new ApiService();
