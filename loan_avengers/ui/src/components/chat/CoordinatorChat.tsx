import { useState, useEffect, useRef } from 'react';
import type { ChatMessage, CoordinatorResponse, QuickReplyOption } from '../../types';
import { LogViewer } from './LogViewer';

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
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(false);
  const [quickReplies, setQuickReplies] = useState<QuickReplyOption[]>([]);
  const [showPersonalInfoForm, setShowPersonalInfoForm] = useState(false);
  const [personalInfo, setPersonalInfo] = useState({ name: '', email: '', idLast4: '' });
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
      sender: 'coordinator',
      message: "Hi there! I'm Cap-ital America, and I can do this all day... help you buy your dream home! 🦸‍♂️🏠\n\nLet's make this quick! Just 4 simple steps.\n\nFirst: What's your target home purchase price? (All amounts in USD)",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);

    // Set initial quick replies for home price
    setQuickReplies([
      {label: "Under $200K", value: "150000", icon: "🏠"},
      {label: "$200K - $400K", value: "300000", icon: "🏡"},
      {label: "$400K - $600K", value: "500000", icon: "🏘️"},
      {label: "$600K - $1M", value: "800000", icon: "🏰"},
      {label: "Over $1M", value: "1200000", icon: "🏛️"}
    ]);
  }, []);


  const handleQuickReply = async (option: QuickReplyOption) => {
    // Clear quick replies immediately
    setQuickReplies([]);

    // Add user's selection to chat (show the label for better UX)
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      message: option.label, // Show label in chat bubble
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: ChatMessage = {
      id: 'typing',
      sender: 'coordinator',
      message: 'Cap-ital America is typing...',
      timestamp: new Date(),
      typing: true,
    };
    setMessages(prev => [...prev, typingMessage]);

    try {
      // Call API with the value directly (not the label)
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: String(option.value), // Send VALUE to backend
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: CoordinatorResponse & { session_id: string } = await response.json();

      // Store session ID for conversation continuity
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));

      // Add Cap-ital America's response
      const coordinatorMessage: ChatMessage = {
        id: `coordinator-${Date.now()}`,
        sender: 'coordinator',
        message: data.message,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, coordinatorMessage]);

      // Update progress
      onProgressUpdate(data.completion_percentage);

      // Update quick replies if provided
      if (data.quick_replies && data.quick_replies.length > 0) {
        setQuickReplies(data.quick_replies);
      }

      // Show personal info form when completion reaches 75%
      if (data.completion_percentage >= 75 && data.completion_percentage < 100) {
        setShowPersonalInfoForm(true);
      }

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
        sender: 'coordinator',
        message: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateDummyData = () => {
    const dummyNames = [
      'Tony Stark', 'Steve Rogers', 'Natasha Romanoff', 'Bruce Banner', 'Thor Odinson',
      'Peter Parker', 'Wanda Maximoff', 'Vision Android', 'Scott Lang', 'Hope van Dyne'
    ];
    const dummyEmails = [
      'ironman@avengers.com', 'cap@avengers.com', 'blackwidow@avengers.com', 'hulk@avengers.com',
      'thor@asgard.com', 'spidey@avengers.com', 'scarlet@avengers.com', 'vision@avengers.com',
      'antman@avengers.com', 'wasp@avengers.com'
    ];

    const randomIndex = Math.floor(Math.random() * dummyNames.length);
    const randomLast4 = Math.floor(1000 + Math.random() * 9000).toString();

    setPersonalInfo({
      name: dummyNames[randomIndex],
      email: dummyEmails[randomIndex],
      idLast4: randomLast4
    });
  };

  const handlePersonalInfoSubmit = async () => {
    if (!personalInfo.name.trim() || !personalInfo.email.trim() || !personalInfo.idLast4.trim()) {
      alert('Please fill in all fields');
      return;
    }

    // Hide form
    setShowPersonalInfoForm(false);

    // Show user's form data as a chat bubble
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      message: `Name: ${personalInfo.name}\nEmail: ${personalInfo.email}\nID Last 4: ${personalInfo.idLast4}`,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Add a smooth transition delay for better UX (1 second)
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Set loading state
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: ChatMessage = {
      id: 'typing',
      sender: 'coordinator',
      message: 'Cap-ital America is assembling the team...',
      timestamp: new Date(),
      typing: true,
    };
    setMessages(prev => [...prev, typingMessage]);

    try {
      // Format message as JSON expected by backend state machine
      const formDataJson = JSON.stringify({
        name: personalInfo.name,
        email: personalInfo.email,
        idLast4: personalInfo.idLast4
      });

      // Call API to complete application and trigger workflow
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: formDataJson,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: CoordinatorResponse & { session_id: string } = await response.json();

      // Store session ID
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));

      // Add Cap-ital America's response
      const coordinatorMessage: ChatMessage = {
        id: `coordinator-${Date.now()}`,
        sender: 'coordinator',
        message: data.message,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, coordinatorMessage]);

      // Update progress to 100%
      onProgressUpdate(data.completion_percentage || 100);

      // Trigger application complete with collected data
      if (data.action === 'ready_for_processing' || data.completion_percentage === 100) {
        onApplicationComplete(data.collected_data);
      }
    } catch (error) {
      console.error('Failed to submit form:', error);

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => msg.id !== 'typing'));

      // Show error message
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'coordinator',
        message: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto bg-white dark:bg-dark-bg-card rounded-lg shadow-xl border border-gray-200 dark:border-gray-700">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-brand-600 to-primary-600 text-white rounded-t-lg shadow-md">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-2xl animate-bounce-gentle">
            🦸‍♂️
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Cap-ital America - Your Loan Coordinator</h3>
            <p className="text-sm text-white/95">Online and ready to assemble your loan!</p>
          </div>
        </div>

        {/* Geek Mode Toggle Button */}
        <button
          onClick={() => setShowLogs(!showLogs)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 ${
            showLogs
              ? 'bg-green-500 text-white shadow-lg'
              : 'bg-white/20 hover:bg-white/30 text-white'
          }`}
          title="Toggle Geek Mode (System Logs)"
        >
          <span className="text-xl">{showLogs ? '🤓' : '👨‍💻'}</span>
          <span className="text-sm font-semibold">{showLogs ? 'Hide' : 'Geek Mode'}</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900">
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
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-white italic'
                  : 'bg-white dark:bg-[#2d2d3d] text-gray-900 dark:text-white shadow-md border border-gray-200 dark:border-gray-600'
              }`}
            >
              {msg.sender === 'coordinator' && !msg.typing && (
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-lg">🦸‍♂️</span>
                  <span className="font-bold text-xs text-brand-600 dark:text-brand-300">
                    Cap-ital America
                  </span>
                </div>
              )}
              <p className={`text-sm leading-relaxed whitespace-pre-wrap font-normal ${
                msg.sender === 'user'
                  ? 'text-white'
                  : msg.typing
                  ? 'text-gray-700 dark:!text-white'
                  : 'text-gray-900 dark:!text-white'
              }`}>{msg.message}</p>
              <span className={`text-xs mt-2 block ${
                msg.sender === 'user'
                  ? 'text-white/80'
                  : 'text-gray-500 dark:text-white/70'
              }`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Reply Buttons */}
      {quickReplies.length > 0 && (
        <div className="px-6 py-4 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-dark-bg-card border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3 font-semibold">Quick choices:</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {quickReplies.map((option, index) => (
              <button
                key={index}
                onClick={() => handleQuickReply(option)}
                disabled={isLoading}
                className="px-5 py-3 bg-white dark:bg-dark-bg-tertiary border-2 border-brand-500 dark:border-brand-400 text-brand-700 dark:text-brand-200 rounded-lg hover:bg-brand-50 dark:hover:bg-brand-900/30 hover:border-brand-600 dark:hover:border-brand-300 transition-all duration-200 text-base font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {option.icon && <span className="text-xl">{option.icon}</span>}
                <span className="text-brand-700 dark:text-white">{option.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Personal Info Form - Fixed positioning to not overlap */}
      {showPersonalInfoForm && (
        <div className="px-6 py-6 bg-gradient-to-b from-brand-50 to-white dark:from-brand-900/20 dark:to-dark-bg-card border-t border-b border-brand-200 dark:border-brand-700 relative z-10">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-brand-700 dark:text-brand-300 flex items-center space-x-2">
                <span>🦸‍♂️</span>
                <span>Final Step: Your Personal Information</span>
              </h3>
              <button
                onClick={generateDummyData}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-semibold shadow-md hover:shadow-lg transition-all duration-200 flex items-center space-x-2"
                title="Generate dummy test data"
              >
                <span>✨</span>
                <span>Generate Dummy Data</span>
              </button>
            </div>

            <div className="space-y-4">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={personalInfo.name}
                  onChange={(e) => setPersonalInfo({ ...personalInfo, name: e.target.value })}
                  placeholder="e.g., Tony Stark"
                  className="w-full px-4 py-3 border-2 border-brand-300 dark:border-brand-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 dark:focus:ring-brand-400 bg-white dark:bg-dark-bg-tertiary text-gray-900 dark:text-dark-text-primary placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-colors duration-300 text-base"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={personalInfo.email}
                  onChange={(e) => setPersonalInfo({ ...personalInfo, email: e.target.value })}
                  placeholder="e.g., ironman@avengers.com"
                  className="w-full px-4 py-3 border-2 border-brand-300 dark:border-brand-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 dark:focus:ring-brand-400 bg-white dark:bg-dark-bg-tertiary text-gray-900 dark:text-dark-text-primary placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-colors duration-300 text-base"
                />
              </div>

              {/* ID Last 4 */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Last 4 Digits of Government ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={personalInfo.idLast4}
                  onChange={(e) => setPersonalInfo({ ...personalInfo, idLast4: e.target.value.replace(/\D/g, '').slice(0, 4) })}
                  placeholder="e.g., 1234"
                  maxLength={4}
                  className="w-full px-4 py-3 border-2 border-brand-300 dark:border-brand-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 dark:focus:ring-brand-400 bg-white dark:bg-dark-bg-tertiary text-gray-900 dark:text-dark-text-primary placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-colors duration-300 text-base"
                />
              </div>

              {/* Next Button - Changed from Submit Application */}
              <div className="pt-2">
                <button
                  onClick={handlePersonalInfoSubmit}
                  className="w-full btn-primary px-6 py-4 text-lg font-bold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center space-x-3"
                >
                  <span>Next</span>
                  <span>→</span>
                </button>
              </div>

              <p className="text-xs text-gray-500 dark:text-gray-400 text-center italic">
                All fields are required • Your data is secure and used only for this demo
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Log Viewer */}
      <LogViewer isOpen={showLogs} onClose={() => setShowLogs(false)} sessionId={sessionId} />
    </div>
  );
}