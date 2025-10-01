import { useState, useEffect } from 'react';
import { Layout } from '../../components/layout/Layout';
import { ExperimentalDisclaimer } from '../../components/ui/ExperimentalDisclaimer';
import { CoordinatorChat } from '../../components/chat/CoordinatorChat';
import type { LoanApplication } from '../../types';

/**
 * Application page component - where users interact with the AI team
 * to complete their loan application through conversation.
 */
export function ApplicationPage() {
  const [currentStep, setCurrentStep] = useState<'intro' | 'conversation' | 'processing'>('intro');
  const [application, setApplication] = useState<Partial<LoanApplication>>({
    status: 'draft',
  });
  const [conversationProgress, setConversationProgress] = useState(0);
  const [processingProgress, setProcessingProgress] = useState(25); // Start at 25% (Intake complete)
  const [currentMessage, setCurrentMessage] = useState<{
    agentName: string;
    icon: string;
    text: string;
    state: 'PROCESSING' | 'COMPLETE' | 'TRANSITION';
    progress: number;
  } | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleStartApplication = () => {
    setCurrentStep('conversation');
  };

  const handleSubmitApplication = () => {
    setCurrentStep('processing');
    // TODO: Integrate with backend API
    console.log('Submitting application:', application);
  };

  const handleApplicationComplete = (applicationData: Record<string, any>, session_id: string) => {
    console.log('Application completed by Cap-ital America:', applicationData);
    // Convert Cap-ital America's collected data to LoanApplication format
    setApplication(prev => ({
      ...prev,
      applicantName: applicationData.applicant_name,
      email: applicationData.email,
      phone: applicationData.phone,
      loanAmount: applicationData.loan_amount,
      loanPurpose: applicationData.loan_purpose,
      annualIncome: applicationData.annual_income,
      employmentStatus: applicationData.employment_status,
      status: 'submitted',
    }));

    // Move to processing step - the workflow will auto-progress
    setCurrentStep('processing');
  };

  const handleProgressUpdate = (percentage: number) => {
    setConversationProgress(percentage);
  };

  // Auto-progress through workflow stages when processing starts
  // Total workflow: ~15 seconds (deliberate friction for better UX)
  useEffect(() => {
    if (currentStep !== 'processing') {
      return;
    }

    const messageSequence = [
      // Cap-ital America - Complete (show for 2.5 seconds)
      { delay: 0, message: { agentName: 'Cap-ital America', icon: '🦸‍♂️', text: '🛡️ Mission Complete! Your application data is validated and secure. Everything checks out!', state: 'COMPLETE' as const, progress: 25 } },
      // Handoff to Scarlet Witch-Credit (1s transition with same agent name)
      { delay: 2500, message: { agentName: 'Cap-ital America', icon: '🤝', text: '⚡ Assembling the team... Scarlet Witch-Credit is ready to analyze your credit magic!', state: 'TRANSITION' as const, progress: 25 } },
      // Scarlet Witch-Credit - Processing (show for 2.5s)
      { delay: 3500, message: { agentName: 'Scarlet Witch-Credit', icon: '🦸‍♀️', text: '✨ Channeling my powers to scan your credit reality... detecting financial patterns...', state: 'PROCESSING' as const, progress: 25 } },
      // Scarlet Witch-Credit - Complete (show for 2.5s)
      { delay: 6000, message: { agentName: 'Scarlet Witch-Credit', icon: '🦸‍♀️', text: '💫 Incredible! Your credit profile radiates strength. Payment history is powerful!', state: 'COMPLETE' as const, progress: 50 } },
      // Handoff to Hawk-Income (1s transition)
      { delay: 8500, message: { agentName: 'Scarlet Witch-Credit', icon: '🤝', text: '🎯 Passing the baton to Hawk-Income for precision income targeting...', state: 'TRANSITION' as const, progress: 50 } },
      // Hawk-Income - Processing (show for 2.5s)
      { delay: 9500, message: { agentName: 'Hawk-Income', icon: '🦸', text: '🏹 Eyes on target! Scanning income streams with hawk-eye precision...', state: 'PROCESSING' as const, progress: 50 } },
      // Hawk-Income - Complete (show for 2.5s)
      { delay: 12000, message: { agentName: 'Hawk-Income', icon: '🦸', text: '🎯 Bulls-eye! Income verified and locked on. Your debt-to-income ratio hits the mark!', state: 'COMPLETE' as const, progress: 75 } },
      // Handoff to Doctor Strange-Risk (1s transition)
      { delay: 14500, message: { agentName: 'Hawk-Income', icon: '🤝', text: '🔮 Calling in the Sorcerer Supreme for the final mystical risk assessment...', state: 'TRANSITION' as const, progress: 75 } },
      // Doctor Strange-Risk - Processing (show for 2.5s)
      { delay: 15500, message: { agentName: 'Doctor Strange-Risk', icon: '🦹‍♂️', text: '🌀 By the Vishanti! Peering through 14 million financial futures...', state: 'PROCESSING' as const, progress: 75 } },
      // Doctor Strange-Risk - Complete (final message stays)
      { delay: 18000, message: { agentName: 'Doctor Strange-Risk', icon: '🦹‍♂️', text: '✨ The Eye of Agamotto reveals success! All dimensions align perfectly. 🎉 APPROVED!', state: 'COMPLETE' as const, progress: 100 } },
    ];

    const updateMessage = (newMessage: typeof currentMessage) => {
      // Trigger fade-out animation
      setIsAnimating(true);

      // After fade-out completes, update message and trigger fade-in
      setTimeout(() => {
        setCurrentMessage(newMessage);
        setIsAnimating(false);
      }, 200); // 200ms fade-out duration
    };

    const timers = messageSequence.map(({ delay, message }) =>
      setTimeout(() => {
        updateMessage(message);
        // Update progress bar smoothly
        setProcessingProgress(message.progress);
      }, delay)
    );

    return () => timers.forEach(clearTimeout);
  }, [currentStep]);

  if (currentStep === 'intro') {
    return (
      <Layout title="Making Loan Dreams Come True">
        <div className="animate-fade-in">
          <div className="py-12 min-h-[calc(100vh-200px)] flex items-center">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div className="text-center animate-fade-in-up">
              {/* Compact rectangle switch with Cap-ital America icon */}
              <div className="relative inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-brand-500 via-brand-600 to-accent-600 rounded-full shadow-lg shadow-brand-500/30 mb-6">
                <span className="text-xl mr-2" aria-hidden="true">🦸‍♂️</span>
                <span className="text-white font-semibold text-sm">Cap-ital America AI</span>
                <div className="absolute inset-0 bg-gradient-to-r from-brand-400 to-accent-500 rounded-full blur opacity-20 animate-pulse"></div>
              </div>

              <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-dark-text-primary mb-4 tracking-tight transition-colors duration-300">
                Hi! I'm{' '}
                <span className="relative inline-block">
                  <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-accent-600 bg-clip-text text-transparent">
                    Cap-ital America
                  </span>
                  <span className="absolute -top-1 -right-2 text-base animate-bounce delay-200">🦸‍♂️</span>
                </span>
                , Your Loan Orchestrator
              </h1>

              <p className="text-lg lg:text-xl text-gray-600 dark:text-dark-text-secondary mb-8 max-w-2xl mx-auto leading-relaxed transition-colors duration-300">
                I can do this all day... approve loans! Let's have a natural conversation instead of filling out boring forms. My Avengers team will guide you every step of the way.
              </p>

              {/* Simplified 3-column layout */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto mb-8">
                <div className="flex flex-col items-center p-4 rounded-2xl bg-white/80 dark:bg-dark-bg-card/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:scale-105 transition-all duration-300">
                  <div className="w-12 h-12 bg-gradient-to-br from-brand-400 to-brand-500 rounded-xl flex items-center justify-center mb-3">
                    <span className="text-xl" aria-hidden="true">💬</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary text-sm mb-1 transition-colors duration-300">Natural Chat</h3>
                  <p className="text-gray-600 dark:text-dark-text-secondary text-xs transition-colors duration-300">Talk like friends</p>
                </div>

                <div className="flex flex-col items-center p-4 rounded-2xl bg-white/80 dark:bg-dark-bg-card/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:scale-105 transition-all duration-300">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-500 rounded-xl flex items-center justify-center mb-3">
                    <span className="text-xl" aria-hidden="true">⚡</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary text-sm mb-1 transition-colors duration-300">Real-time Processing</h3>
                  <p className="text-gray-600 dark:text-dark-text-secondary text-xs transition-colors duration-300">Watch your progress</p>
                </div>

                <div className="flex flex-col items-center p-4 rounded-2xl bg-white/80 dark:bg-dark-bg-card/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:scale-105 transition-all duration-300">
                  <div className="w-12 h-12 bg-gradient-to-br from-success-400 to-success-500 rounded-xl flex items-center justify-center mb-3">
                    <span className="text-xl" aria-hidden="true">🎉</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary text-sm mb-1 transition-colors duration-300">Under 2 Minutes</h3>
                  <p className="text-gray-600 dark:text-dark-text-secondary text-xs transition-colors duration-300">Quick decisions</p>
                </div>
              </div>

              <button
                onClick={handleStartApplication}
                className="btn-primary text-lg px-10 py-5 shadow-xl hover:shadow-2xl transform hover:scale-110 transition-all duration-300 group animate-pulse-soft"
              >
                <span>Let's Start Our Conversation!</span>
                <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>
          </div>

          {/* Experimental Disclaimer - Footer */}
          <div className="bg-gray-50 dark:bg-dark-bg-secondary py-4 transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <ExperimentalDisclaimer />
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (currentStep === 'conversation') {
    return (
      <Layout title="Chat with Cap-ital America - Your Loan Orchestrator">
        <div className="py-8">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="animate-fade-in">
              {/* Header Section */}
              <div className="text-center mb-8">
                <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-dark-text-primary mb-4 transition-colors duration-300">
                  Chat with{' '}
                  <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-accent-600 bg-clip-text text-transparent">
                    Cap-ital America
                  </span>
                  🦸‍♂️
                </h1>
                <p className="text-lg text-gray-600 dark:text-dark-text-secondary max-w-2xl mx-auto leading-relaxed transition-colors duration-300">
                  Have a natural conversation with Cap-ital America to collect your loan application details.
                </p>
              </div>

              {/* Coordinator Chat Interface */}
              <CoordinatorChat
                onApplicationComplete={handleApplicationComplete}
                onProgressUpdate={handleProgressUpdate}
              />

              {/* Progress Indicator - Below Chat */}
              <div className="max-w-4xl mx-auto mt-6">
                <div className="bg-white dark:bg-dark-bg-card rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-base font-bold text-gray-900 dark:text-dark-text-primary">
                      Application Progress
                    </span>
                    <span className="text-lg font-bold text-brand-600 dark:text-brand-400">
                      {conversationProgress}% Complete
                    </span>
                  </div>
                  <div className="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 via-primary-500 to-accent-500 rounded-full transition-all duration-500 ease-out shadow-sm"
                      style={{ width: `${conversationProgress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs font-medium text-gray-600 dark:text-gray-400 mt-2">
                    <span>Getting Started</span>
                    <span>Personal Details</span>
                    <span>Loan Information</span>
                    <span>Ready to Process!</span>
                  </div>
                </div>
              </div>

              {/* Quick Tips */}
              <div className="max-w-4xl mx-auto mt-8">
                <div className="card bg-gradient-to-r from-brand-50 to-primary-50 dark:from-dark-bg-tertiary dark:to-dark-bg-tertiary border border-brand-200 dark:border-dark-bg-tertiary">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-4 text-center">
                    💡 Chat Tips
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-2xl mb-2">💬</div>
                      <p className="text-gray-700 dark:text-dark-text-secondary">
                        Talk naturally - Cap-ital America understands conversational language
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl mb-2">🔒</div>
                      <p className="text-gray-700 dark:text-dark-text-secondary">
                        Your information is secure and encrypted
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl mb-2">⚡</div>
                      <p className="text-gray-700 dark:text-dark-text-secondary">
                        Once complete, your application processes instantly
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (currentStep === 'processing') {
    return (
      <Layout title="Processing Your Application">
        <div className="py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center animate-fade-in-up">
              <div className="relative inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-warning-400 via-warning-500 to-brand-500 rounded-2xl shadow-xl shadow-warning-500/30 mb-8 animate-pulse-soft">
                <span className="text-3xl" aria-hidden="true">⚡</span>
                <div className="absolute -inset-2 bg-gradient-to-r from-warning-300 to-brand-400 rounded-3xl blur opacity-20 animate-ping"></div>
                <span className="absolute -top-2 -right-2 text-lg animate-bounce delay-100">✨</span>
                <span className="absolute -bottom-1 -left-2 text-sm animate-pulse delay-300">💫</span>
              </div>

              <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6 tracking-tight">
                Your{' '}
                <span className="relative inline-block">
                  <span className="bg-gradient-to-r from-brand-600 via-accent-600 to-brand-500 bg-clip-text text-transparent">
                    AI Team
                  </span>
                  <span className="absolute -top-1 -right-3 text-lg animate-spin">⭐</span>
                </span>
                {' '}is Working Their{' '}
                <span className="relative inline-block">
                  <span className="bg-gradient-to-r from-warning-500 via-brand-500 to-accent-600 bg-clip-text text-transparent">
                    Magic!
                  </span>
                  <span className="absolute -top-2 -right-2 text-xl animate-pulse">✨</span>
                  <span className="absolute -bottom-1 -left-1 text-sm animate-bounce delay-150">🔮</span>
                </span>
              </h1>

              <p className="text-xl mb-12 max-w-2xl mx-auto leading-relaxed">
                <span className="bg-gradient-to-r from-gray-700 via-gray-900 to-gray-700 bg-clip-text text-transparent font-medium">
                  Please wait while we process your application. This should only take a few moments.
                </span>
              </p>

              {/* Workflow Progress */}
              <div className="card-elevated max-w-4xl mx-auto mb-8">
                <h2 className="text-2xl font-semibold mb-8 text-center">
                  <span className="bg-gradient-to-r from-gray-800 via-gray-900 to-gray-800 bg-clip-text text-transparent">
                    Processing Workflow
                  </span>
                </h2>

                {/* Progress Steps */}
                <div className="relative">
                  {/* Progress Line */}
                  <div className="absolute top-8 left-0 right-0 h-0.5 bg-gray-200">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-brand-600 rounded-full transition-all duration-1000"
                      style={{width: `${(processingProgress / 100) * 100}%`}}
                    ></div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
                    {/* Intake Agent */}
                    <div className={`workflow-step ${processingProgress >= 25 ? 'completed' : 'pending'} animate-workflow-step`}>
                      <div className="flex flex-col items-center">
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-lg ${
                          processingProgress >= 25
                            ? 'bg-gradient-to-br from-success-500 to-success-600'
                            : 'bg-gray-200'
                        }`}>
                          {processingProgress >= 25 ? (
                            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          ) : (
                            <span className="text-2xl opacity-50" aria-hidden="true">📋</span>
                          )}
                        </div>
                        <h3 className={`font-semibold mb-1 ${processingProgress >= 25 ? 'text-gray-900' : 'text-gray-500'}`}>Intake</h3>
                        <p className={`text-sm font-medium ${processingProgress >= 25 ? 'text-success-600' : 'text-gray-400'}`}>
                          {processingProgress >= 25 ? 'Complete' : 'Waiting...'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1 text-center">Application received and validated</p>
                      </div>
                    </div>

                    {/* Credit Agent */}
                    <div className={`workflow-step ${
                      processingProgress >= 50 ? 'completed' : processingProgress >= 25 ? 'active' : 'pending'
                    } animate-workflow-step`} style={{animationDelay: '0.2s'}}>
                      <div className="flex flex-col items-center">
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-lg ${
                          processingProgress >= 50
                            ? 'bg-gradient-to-br from-success-500 to-success-600'
                            : processingProgress >= 25
                            ? 'bg-gradient-to-br from-brand-500 to-brand-600 animate-pulse-soft'
                            : 'bg-gray-200'
                        }`}>
                          {processingProgress >= 50 ? (
                            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          ) : (
                            <span className={`text-2xl ${processingProgress >= 25 ? '' : 'opacity-50'}`} aria-hidden="true">🦸‍♀️</span>
                          )}
                        </div>
                        <h3 className={`font-semibold mb-1 ${processingProgress >= 25 ? 'text-gray-900' : 'text-gray-500'}`}>Credit Analysis</h3>
                        <p className={`text-sm font-medium ${
                          processingProgress >= 50 ? 'text-success-600' : processingProgress >= 25 ? 'text-brand-600' : 'text-gray-400'
                        }`}>
                          {processingProgress >= 50 ? 'Complete' : processingProgress >= 25 ? 'In Progress...' : 'Waiting...'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1 text-center">Scarlet Witch-Credit is analyzing your credit profile</p>
                      </div>
                    </div>

                    {/* Income Agent */}
                    <div className={`workflow-step ${
                      processingProgress >= 75 ? 'completed' : processingProgress >= 50 ? 'active' : 'pending'
                    } animate-workflow-step`} style={{animationDelay: '0.4s'}}>
                      <div className="flex flex-col items-center">
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-lg ${
                          processingProgress >= 75
                            ? 'bg-gradient-to-br from-success-500 to-success-600'
                            : processingProgress >= 50
                            ? 'bg-gradient-to-br from-brand-500 to-brand-600 animate-pulse-soft'
                            : 'bg-gray-200'
                        }`}>
                          {processingProgress >= 75 ? (
                            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          ) : (
                            <span className={`text-2xl ${processingProgress >= 50 ? '' : 'opacity-50'}`} aria-hidden="true">🦸</span>
                          )}
                        </div>
                        <h3 className={`font-semibold mb-1 ${processingProgress >= 50 ? 'text-gray-900' : 'text-gray-500'}`}>Income Verification</h3>
                        <p className={`text-sm font-medium ${
                          processingProgress >= 75 ? 'text-success-600' : processingProgress >= 50 ? 'text-brand-600' : 'text-gray-400'
                        }`}>
                          {processingProgress >= 75 ? 'Complete' : processingProgress >= 50 ? 'In Progress...' : 'Waiting...'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1 text-center">Hawk-Income will verify your income</p>
                      </div>
                    </div>

                    {/* Risk Agent */}
                    <div className={`workflow-step ${
                      processingProgress >= 100 ? 'completed' : processingProgress >= 75 ? 'active' : 'pending'
                    } animate-workflow-step`} style={{animationDelay: '0.6s'}}>
                      <div className="flex flex-col items-center">
                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-lg ${
                          processingProgress >= 100
                            ? 'bg-gradient-to-br from-success-500 to-success-600'
                            : processingProgress >= 75
                            ? 'bg-gradient-to-br from-brand-500 to-brand-600 animate-pulse-soft'
                            : 'bg-gray-200'
                        }`}>
                          {processingProgress >= 100 ? (
                            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          ) : (
                            <span className={`text-2xl ${processingProgress >= 75 ? '' : 'opacity-50'}`} aria-hidden="true">🦹‍♂️</span>
                          )}
                        </div>
                        <h3 className={`font-semibold mb-1 ${processingProgress >= 75 ? 'text-gray-900' : 'text-gray-500'}`}>Risk Assessment</h3>
                        <p className={`text-sm font-medium ${
                          processingProgress >= 100 ? 'text-success-600' : processingProgress >= 75 ? 'text-brand-600' : 'text-gray-400'
                        }`}>
                          {processingProgress >= 100 ? 'Complete' : processingProgress >= 75 ? 'In Progress...' : 'Waiting...'}
                        </p>
                        <p className="text-xs text-gray-400 mt-1 text-center">Doctor Strange-Risk will assess overall risk</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Single Agent Message Display - Hide when complete */}
                {currentMessage && processingProgress < 100 && (
                  <div className="mt-10">
                    <h3 className="text-lg font-semibold text-center mb-4">
                      <span className="bg-gradient-to-r from-brand-600 via-accent-600 to-brand-500 bg-clip-text text-transparent">
                        💬 What Your AI Team Says
                      </span>
                    </h3>
                    <div
                      className={`min-h-[100px] sm:min-h-[120px] ${isAnimating ? 'message-fade-out' : 'message-fade-in'}`}
                      role="status"
                      aria-live="polite"
                      aria-atomic="true"
                      aria-label={`${currentMessage.agentName} says: ${currentMessage.text}. Progress: ${currentMessage.progress} percent complete.`}
                    >
                      <div className={`rounded-lg p-4 sm:p-6 border transition-colors duration-200 ${
                        currentMessage.state === 'COMPLETE'
                          ? 'bg-gradient-to-r from-success-50 to-green-50 border-success-200'
                          : currentMessage.state === 'TRANSITION'
                          ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
                          : 'bg-gradient-to-r from-gray-50 to-blue-50 border-brand-200'
                      }`}>
                        <div className="flex items-start space-x-3">
                          <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                            currentMessage.state === 'COMPLETE'
                              ? 'bg-gradient-to-br from-success-500 to-success-600'
                              : currentMessage.state === 'TRANSITION'
                              ? 'bg-gradient-to-br from-blue-500 to-indigo-600'
                              : 'bg-gradient-to-br from-brand-500 to-brand-600'
                          }`}>
                            <span className="text-xl sm:text-2xl">{currentMessage.icon}</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold text-gray-900 text-sm sm:text-base mb-1">
                              {currentMessage.agentName}
                            </p>
                            <p className={`text-gray-700 text-sm sm:text-base leading-relaxed ${
                              currentMessage.state === 'PROCESSING' ? 'processing-dots' : ''
                            }`}>
                              {currentMessage.text}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* View Results Button - Show when workflow completes */}
                {processingProgress === 100 && (
                  <div className="mt-10 text-center animate-fade-in-up">
                    <div className="mb-6">
                      <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-success-500 to-success-600 rounded-full shadow-xl mb-4 animate-bounce-gentle">
                        <span className="text-4xl">🎉</span>
                      </div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        <span className="bg-gradient-to-r from-success-600 to-success-700 bg-clip-text text-transparent">
                          Application Approved!
                        </span>
                      </h3>
                      <p className="text-gray-600 text-lg">
                        Your loan has been approved. View your results below!
                      </p>
                    </div>
                    <button
                      onClick={() => window.location.href = '/results'}
                      className="btn-primary text-lg px-10 py-5 shadow-xl hover:shadow-2xl transform hover:scale-110 transition-all duration-300"
                    >
                      <span>View Your Results</span>
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </button>
                  </div>
                )}

                {/* Overall Progress */}
                <div className="mt-10 pt-6 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                    <span className="text-sm font-medium text-brand-600">{processingProgress}% Complete</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill transition-all duration-1000" style={{width: `${processingProgress}%`}}></div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return null;
}