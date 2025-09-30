import { useState, useEffect, useRef } from 'react';
import type { ChatMessage, RileyResponse } from '../../types';

interface CoordinatorChatProps {
  onApplicationComplete: (applicationData: Record<string, any>) => void;
  onProgressUpdate: (percentage: number) => void;
}

/**
 * Coordinator Chat Component - Conversational loan application interface
 *
 * This component provides a chat interface for users to interact with Cap-ital America,
 * the AI coordinator who collects loan application details through natural conversation.
 */
export function CoordinatorChat({ onApplicationComplete, onProgressUpdate }: CoordinatorChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send initial greeting from Cap-ital America when component mounts
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome-1',
      sender: 'riley',
      message: "Hi! I'm Cap-ital America, your AI loan coordinator! 🦸‍♂️ I'm an AI assistant designed to help gather your loan application details through friendly conversation. I can do this all day... approve loans! Let's chat and I'll collect the information we need. What type of loan are you interested in?",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      message: inputMessage,
      timestamp: new Date(),
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: ChatMessage = {
      id: 'typing',
      sender: 'riley',
      message: 'Riley is typing...',
      timestamp: new Date(),
      typing: true,
    };
    setMessages(prev => [...prev, typingMessage]);

    try {
      // Call unified workflow API
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: inputMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: RileyResponse & { session_id: string } = await response.json();

      // Store session ID for conversation continuity
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));

      // Add Riley's response
      const rileyMessage: ChatMessage = {
        id: `riley-${Date.now()}`,
        sender: 'riley',
        message: data.message,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, rileyMessage]);

      // Update progress
      onProgressUpdate(data.completion_percentage);

      // Check if application is complete
      if (data.action === 'completed' && data.completion_percentage === 100) {
        onApplicationComplete(data.collected_data);
      }
    } catch (error) {
      console.error('Failed to send message:', error);

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));

      // Show error message
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'riley',
        message: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto bg-white dark:bg-dark-bg-card rounded-lg shadow-xl border border-gray-200 dark:border-gray-700">
      {/* Chat Header */}
      <div className="flex items-center px-6 py-4 bg-gradient-to-r from-brand-600 to-primary-600 text-white rounded-t-lg shadow-md">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-2xl animate-bounce-gentle">
            🦸‍♂️
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Cap-ital America - Your Loan Coordinator</h3>
            <p className="text-sm text-white/95">Online and ready to assemble your loan!</p>
          </div>
        </div>
      </div>

      {/* AI Disclaimer Banner */}
      <div className="px-6 py-3 bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800/50">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 mt-0.5">
            <svg className="w-5 h-5 text-amber-600 dark:text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1 text-xs text-amber-800 dark:text-amber-200">
            <p className="font-semibold mb-1">AI Assistant Notice</p>
            <p className="text-amber-700 dark:text-amber-300">
              Cap-ital America is an AI assistant powered by large language models. While designed to help with loan applications, AI can make mistakes.
              Please verify all important information and consult with a human loan officer for final decisions.
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
          >
            <div
              className={`max-w-[70%] rounded-2xl px-5 py-3 ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-br from-brand-600 to-brand-700 text-white shadow-lg'
                  : msg.typing
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 italic'
                  : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-50 shadow-md border border-gray-200 dark:border-gray-600'
              }`}
            >
              {msg.sender === 'riley' && !msg.typing && (
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-lg">🦸‍♂️</span>
                  <span className="font-bold text-sm text-brand-600 dark:text-brand-300">
                    Cap-ital America
                  </span>
                </div>
              )}
              <p className="text-base leading-relaxed whitespace-pre-wrap">{msg.message}</p>
              <span className={`text-xs mt-2 block ${
                msg.sender === 'user'
                  ? 'text-white/80'
                  : 'text-gray-500 dark:text-gray-400'
              }`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-6 py-4 bg-white dark:bg-dark-bg-card border-t border-gray-200 dark:border-gray-700/50 rounded-b-lg">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 dark:focus:ring-brand-400 bg-white dark:bg-dark-bg-tertiary text-gray-900 dark:text-dark-text-primary placeholder:text-gray-500 dark:placeholder:text-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300"
            aria-label="Chat message input"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="btn-primary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            aria-label="Send message"
          >
            <span>Send</span>
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-500 dark:text-dark-text-tertiary mt-2">
          Press Enter to send • Shift + Enter for new line
        </p>
      </div>
    </div>
  );
}