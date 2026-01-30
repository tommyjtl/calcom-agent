'use client';

import { useState, useEffect } from 'react';

import MessageArea from '../components/MessageArea';
import UserInputArea from '../components/UserInputArea';
import UserInfoForm from '../components/UserInfoForm';
import UserProfile from '../components/UserProfile';
import { apiService, type ToolResult } from '../services/api';
import { formatToolResultAsMarkdown } from '../store/toolResultFormatters';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

interface UserInfo {
  name: string;
  email: string;
  timezone: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [error, setError] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  // Load user info from localStorage on component mount
  useEffect(() => {
    const initializeApp = () => {
      try {
        const savedUserInfo = localStorage.getItem('calcom_user_info');
        if (savedUserInfo) {
          setUserInfo(JSON.parse(savedUserInfo));
        }
      } catch (error) {
        console.error('Failed to parse saved user info:', error);
        localStorage.removeItem('calcom_user_info');
      } finally {
        setIsInitializing(false);
      }
    };

    // Add a small delay to show the loading screen briefly
    const timer = setTimeout(initializeApp, 100);

    return () => clearTimeout(timer);
  }, []);

  // Test API connection when user info is available
  useEffect(() => {
    if (!userInfo) return;

    const testConnection = async () => {
      try {
        await apiService.healthCheck();
        // console.log('API connection successful');
      } catch (error) {
        console.error('API connection failed:', error);
        setError('Failed to connect to the API server.');
      }
    };

    testConnection();
  }, [userInfo]);

  const handleUserInfoSubmit = (info: UserInfo) => {
    setUserInfo(info);
    localStorage.setItem('calcom_user_info', JSON.stringify(info));
  };

  const handleLogout = () => {
    localStorage.removeItem('calcom_user_info');
    window.location.reload();
  };

  const handleSendMessage = async (messageText: string) => {
    if (!userInfo) return;

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Make API call with user context
      const response = await apiService.chat({
        message: `User info: Name: ${userInfo.name}, 
        Email: ${userInfo.email}, 
        Timezone: ${userInfo.timezone}\n\n
        User message: ${messageText}`,
        session_id: sessionId,
      });

      // console.log('API Response:', response);

      // Determine the response text and tool results
      let responseText = '';

      if (response.message) {
        responseText = response.message;
      } else if (response.tool_results && response.tool_results.length > 0) {
        // Debug: log the raw tool results structure
        // console.log('Raw tool_results:', response.tool_results);

        // Format tool results as markdown and append to response text
        const toolResultsMarkdown = response.tool_results.map((result: ToolResult) => {
          // console.log('Processing tool result:', result);
          return formatToolResultAsMarkdown(result);
        }).join('\n\n---\n\n');

        responseText = toolResultsMarkdown;
      } else {
        responseText = 'No response received from server';
      }

      // Add bot response
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        sender: 'bot',
        // No longer need toolResults since we're formatting as markdown
      };

      // console.log('Bot Message:', botMessage);
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat API error:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error while processing your message. Server is not available at the moment',
        sender: 'bot',
      };

      setMessages(prev => [...prev, errorMessage]);
      setError('Failed to send message. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading screen while initializing
  if (isInitializing) {
    return (
      <div className="min-h-screen bg-gray-400 flex items-center justify-center p-4 font-sans">
        <div className="bg-white rounded-lg shadow-lg p-8 flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <h2 className="text-lg font-semibold text-gray-800 mb-2">Cal.com Assistant</h2>
          <p className="text-sm text-gray-600">Loading your information...</p>
        </div>
      </div>
    );
  }

  // Show user info form if no user info is available
  if (!userInfo) {
    return <UserInfoForm onSubmit={handleUserInfoSubmit} />;
  }

  return (
    <div className="min-h-screen bg-gray-400 flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-4xl h-[80vh] bg-white rounded-lg shadow-lg flex flex-col">
        {/* Header */}
        <div className="p-4 bg-white border-b border-gray-200 rounded-t-lg flex justify-between items-center">
          <h1 className="text-md font-semibold text-gray-800">Cal.com Scheduling Assistant</h1>
          <div className="flex items-center space-x-3">
            <UserProfile userInfo={userInfo} />
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors border border-gray-300"
            >
              Logout
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-100 border-b border-red-200 text-red-700 text-sm">
            <p>{error}</p>
          </div>
        )}
        <MessageArea messages={messages} isLoading={isLoading} />
        <UserInputArea
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          isDisabled={!!error}
        />
      </div>
    </div>
  );
}
