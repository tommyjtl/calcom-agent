'use client';

import { useEffect, useRef } from 'react';
import MessageBox from './MessageBox';
import MessageSkeleton from './MessageSkeleton';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'bot';
}

interface MessageAreaProps {
    messages: Message[];
    isLoading?: boolean;
}

export default function MessageArea({ messages, isLoading = false }: MessageAreaProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to the top of the last message when messages change or loading state changes
    useEffect(() => {
        if (scrollRef.current && messages.length > 0) {
            // Find the last message element
            const messageElements = scrollRef.current.querySelectorAll('[data-message-id]');
            const lastMessageElement = messageElements[messageElements.length - 1] as HTMLElement;

            if (lastMessageElement) {
                // Scroll to the top of the last message
                // const containerRect = scrollRef.current.getBoundingClientRect();
                // const messageRect = lastMessageElement.getBoundingClientRect();
                const scrollOffset = lastMessageElement.offsetTop - scrollRef.current.offsetTop;

                scrollRef.current.scrollTop = scrollOffset;
            }
        }
    }, [messages, isLoading]);

    return (
        <div ref={scrollRef} className="flex-1 overflow-y-auto py-5 px-5 bg-gray-50">
            {messages.length === 0 && !isLoading ? (
                <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                    <p>Start a conversation...</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {messages.map((message) => (
                        <MessageBox
                            key={message.id}
                            message={message.text}
                            sender={message.sender}
                            messageId={message.id}
                        />
                    ))}
                    {isLoading && <MessageSkeleton />}
                </div>
            )}
        </div>
    );
}
