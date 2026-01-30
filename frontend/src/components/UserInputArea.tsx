'use client';

import { useState, useEffect, useRef } from 'react';

interface UserInputAreaProps {
    onSendMessage: (message: string) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
}

// Example messages for quick access
const EXAMPLE_MESSAGES = [
    "List all events I've booked",
    "Book an meeting with Tommy for 30 minutes next Mon 1pm",
    "Cancel the 30-minute meeting with Tommy next Mon 1pm",
];

export default function UserInputArea({ onSendMessage, isLoading = false, isDisabled = false }: UserInputAreaProps) {
    const [message, setMessage] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-focus the textarea when LLM finishes responding
    useEffect(() => {
        if (!isLoading && !isDisabled) {
            textareaRef.current?.focus();
        }
    }, [isLoading, isDisabled]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (message.trim() && !isLoading && !isDisabled) {
            onSendMessage(message.trim());
            setMessage('');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading && !isDisabled) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleExampleClick = (exampleMessage: string) => {
        if (!isLoading && !isDisabled) {
            onSendMessage(exampleMessage);
        }
    };

    return (
        <div className="p-4 bg-white border-t border-gray-200 rounded-b-lg">
            {/* Example messages row */}
            <div className="mb-3">
                <p className="text-xs text-gray-500 mb-2">Quick examples:</p>
                <div className="flex flex-wrap gap-2">
                    {EXAMPLE_MESSAGES.map((example, index) => (
                        <button
                            key={index}
                            onClick={() => handleExampleClick(example)}
                            disabled={isLoading || isDisabled}
                            className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full border border-gray-300 transition-colors whitespace-nowrap disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                        >
                            {example}
                        </button>
                    ))}
                </div>
            </div>

            {/* Input form */}
            <form onSubmit={handleSubmit} className="flex gap-2">
                <textarea
                    ref={textareaRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={isLoading ? "Processing your request..." : isDisabled ? "Connection error - please refresh" : "Type your message..."}
                    disabled={isLoading || isDisabled}
                    className="text-sm flex-1 p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
                    rows={1}
                    style={{ maxHeight: '120px' }}
                />
                <button
                    type="submit"
                    disabled={!message.trim() || isLoading || isDisabled}
                    className="text-sm px-4 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                    {isLoading ? 'Sending...' : isDisabled ? 'Disabled' : 'Send'}
                </button>
            </form>
        </div>
    );
}
