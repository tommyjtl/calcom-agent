'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface MessageBoxProps {
    message: string;
    sender: 'user' | 'bot';
    messageId?: string;
}

export default function MessageBox({ message, sender, messageId }: MessageBoxProps) {
    const [, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(message);
            setCopied(true);
            // Reset the copied state after 2 seconds
            setTimeout(() => setCopied(false), 2000);
        } catch (error) {
            console.error('Failed to copy message:', error);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = message;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            } catch (fallbackError) {
                console.error('Fallback copy also failed:', fallbackError);
            }
            document.body.removeChild(textArea);
        }
    };
    return (
        <div className={`w-full flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`} data-message-id={messageId}>
            <div
                onClick={handleCopy}
                className={`max-w-[70%] p-3 rounded-lg cursor-pointer transition-all duration-200 relative ${sender === 'user'
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                    }`}
                title="Click to copy message"
            >

                <div className="text-sm prose prose-sm max-w-none">
                    <ReactMarkdown
                        components={{
                            // Customize paragraph styling
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            // Customize list styling
                            ul: ({ children }) => <ul className="list-disc list-inside ms-2 mb-2 last:mb-0">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal list-inside ms-2 mb-2 last:mb-0">{children}</ol>,
                            li: ({ children }) => <li className="mb-1">{children}</li>,
                            // Customize code styling
                            code: ({ children, className }) => {
                                const isInline = !className;
                                return isInline ? (
                                    <code className={`px-1 py-0.5 rounded text-xs font-mono ${sender === 'user'
                                        ? 'bg-blue-600 text-blue-100'
                                        : 'bg-gray-300 text-gray-800'
                                        }`}>
                                        {children}
                                    </code>
                                ) : (
                                    <code className={`block p-2 rounded text-xs font-mono whitespace-pre-wrap ${sender === 'user'
                                        ? 'bg-blue-600 text-blue-100'
                                        : 'bg-gray-300 text-gray-800'
                                        }`}>
                                        {children}
                                    </code>
                                );
                            },
                            // Customize link styling
                            a: ({ children, href }) => (
                                <a
                                    href={href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={`underline ${sender === 'user'
                                        ? 'text-blue-100 hover:text-white'
                                        : 'text-blue-600 hover:text-blue-800'
                                        }`}
                                >
                                    {children}
                                </a>
                            ),
                            // Customize heading styling
                            h1: ({ children }) => <h1 className="text-base font-bold mb-2">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-sm font-bold mb-2">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
                            // Customize strong/bold styling
                            strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                            // Customize emphasis/italic styling
                            em: ({ children }) => <em className="italic">{children}</em>,
                        }}
                    >
                        {message}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
}
