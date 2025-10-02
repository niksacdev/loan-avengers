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
  const [_application, setApplication] = useState<Partial<LoanApplication>>({
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
  const [finalDecision, setFinalDecision] = useState<any>(null); // Store final decision from SSE
  const [showCompilingAnimation, setShowCompilingAnimation] = useState(false); // Show compiling animation after Risk Analyzer

  const handleStartApplication = () => {
    setCurrentStep('conversation');
  };

  const handleApplicationComplete = (applicationData: Record<string, any>, session_id: string) => {
    console.log('Application completed by Cap-ital America:', applicationData);
    console.log('Session ID:', session_id);

    // Convert Cap-ital America's collected data to LoanApplication format
    const fullApplication = {
      applicantName: applicationData.applicant_name,
      email: applicationData.email,
      phone: applicationData.phone,
      loanAmount: applicationData.loan_amount,
      loanPurpose: applicationData.loan_purpose,
      annualIncome: applicationData.annual_income,
      employmentStatus: applicationData.employment_status,
      status: 'submitted',
      session_id: session_id,  // Include session_id for SSE endpoint
      ...applicationData,  // Include all collected data for API
    };

    setApplication(fullApplication);

    // Move to processing step - the SSE workflow will start automatically
    setCurrentStep('processing');
  };

  const handleProgressUpdate = (percentage: number) => {
    setConversationProgress(percentage);
  };

  // Connect to SSE stream when processing starts
  useEffect(() => {
    if (currentStep !== 'processing' || !_application) {
      console.log('SSE not starting:', { currentStep, hasApplication: !!_application });
      return;
    }

    console.log('Starting SSE connection with application:', _application);

    const connectToSSE = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const sseEndpoint = `${apiUrl}/api/workflow/stream`;

        console.log('Connecting to SSE endpoint:', sseEndpoint);
        console.log('Sending data:', {
          application_data: _application,
          session_id: _application.session_id || 'unknown',
        });

        // Call API to start SSE workflow stream
        const response = await fetch(sseEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            application_data: _application,
            session_id: _application.session_id || 'unknown',
          }),
        });

        console.log('SSE Response status:', response.status);

        if (!response.ok) {
          throw new Error(`SSE connection failed: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('Response body is not readable');
        }

        // Read SSE stream
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // Decode chunk and parse SSE events
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.substring(6));

                // Map agent names to icons
                const agentIcons: Record<string, string> = {
                  'Intake_Agent': '🦸‍♂️',
                  'Credit_Assessor': '🦸‍♀️',
                  'Income_Verifier': '🦸',
                  'Risk_Analyzer': '🦹‍♂️',
                  'System': '⚠️',
                };

                // Map status to display state
                const displayState = eventData.status === 'completed' ? 'COMPLETE' :
                                   eventData.status === 'error' ? 'TRANSITION' :
                                   'PROCESSING';

                // Update message with real agent data
                setCurrentMessage({
                  agentName: eventData.agent_name,
                  icon: agentIcons[eventData.agent_name] || '🤖',
                  text: eventData.message,
                  state: displayState as 'PROCESSING' | 'COMPLETE' | 'TRANSITION',
                  progress: eventData.completion_percentage,
                });

                // Update progress bar
                setProcessingProgress(eventData.completion_percentage);

                // Show compiling animation when progress hits 100%
                if (eventData.completion_percentage === 100 && !showCompilingAnimation && !finalDecision) {
                  setShowCompilingAnimation(true);
                }

                // Store decision and navigate when completed
                if (eventData.status === 'completed' && eventData.completion_percentage === 100) {
                  // Store final decision from SSE event in session storage for ResultsPage
                  if (eventData.assessment_data?.decision) {
                    const decision = eventData.assessment_data.decision;
                    sessionStorage.setItem('loanDecision', JSON.stringify(decision));
                    console.log('Decision received:', decision);
                    console.log('Decision reasoning field:', decision.reasoning);

                    // After 2 seconds (compiling already showing), hide compiling and show the final decision
                    setTimeout(() => {
                      setShowCompilingAnimation(false);
                      setFinalDecision(decision); // Store in component state for dynamic message
                    }, 2000);

                    // Navigate to results page after 7 seconds total (2s compiling + 5s viewing decision)
                    setTimeout(() => {
                      window.location.href = '/results';
                    }, 7000);
                  } else {
                    console.error('No decision data in final event:', eventData);
                  }
                }
              } catch (e) {
                console.error('Failed to parse SSE event:', e);
              }
            }
          }
        }
      } catch (error) {
        console.error('SSE connection error:', error);
        setCurrentMessage({
          agentName: 'System',
          icon: '⚠️',
          text: `Connection error: ${error}. Please refresh and try again.`,
          state: 'TRANSITION',
          progress: 0,
        });
      }
    };

    connectToSSE();
  }, [currentStep, _application]);

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

              <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-6 tracking-tight">
                <span className="text-gray-900 dark:text-gray-100">Your</span>{' '}
                <span className="relative inline-block">
                  <span className="bg-gradient-to-r from-brand-600 via-accent-600 to-brand-500 bg-clip-text text-transparent">
                    AI Team
                  </span>
                  <span className="absolute -top-1 -right-3 text-lg animate-spin">⭐</span>
                </span>
                {' '}<span className="text-gray-900 dark:text-gray-100">is Working Their</span>{' '}
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

                {/* Compiling Results Animation - Show immediately after completion */}
                {showCompilingAnimation && (
                  <div className="mt-10 text-center animate-fade-in-up">
                    <div className="mb-6">
                      <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-500 to-accent-600 rounded-full shadow-xl mb-4">
                        <span className="text-4xl animate-spin">⚙️</span>
                      </div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        <span className="bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                          Compiling Your Results...
                        </span>
                      </h3>
                      <p className="text-gray-600 text-lg">
                        Finalizing your loan decision
                      </p>
                    </div>
                  </div>
                )}

                {/* View Results Button - Show when workflow completes */}
                {processingProgress === 100 && finalDecision && (
                  <div className="mt-10 text-center animate-fade-in-up">
                    <div className="mb-6">
                      {/* Dynamic icon based on decision status */}
                      <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full shadow-xl mb-4 animate-bounce-gentle ${
                        finalDecision.status === 'approved'
                          ? 'bg-gradient-to-br from-success-500 to-success-600'
                          : finalDecision.status === 'manual_review'
                          ? 'bg-gradient-to-br from-warning-500 to-warning-600'
                          : finalDecision.status === 'conditional'
                          ? 'bg-gradient-to-br from-info-500 to-info-600'
                          : 'bg-gradient-to-br from-error-500 to-error-600'
                      }`}>
                        <span className="text-4xl">
                          {finalDecision.status === 'approved' ? '🎉' :
                           finalDecision.status === 'manual_review' ? '🔍' :
                           finalDecision.status === 'conditional' ? '✅' : '📋'}
                        </span>
                      </div>
                      {/* Dynamic title based on decision status */}
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        <span className={`bg-gradient-to-r bg-clip-text text-transparent ${
                          finalDecision.status === 'approved'
                            ? 'from-success-600 to-success-700'
                            : finalDecision.status === 'manual_review'
                            ? 'from-warning-600 to-warning-700'
                            : finalDecision.status === 'conditional'
                            ? 'from-info-600 to-info-700'
                            : 'from-gray-600 to-gray-700'
                        }`}>
                          {finalDecision.status === 'approved' ? 'Application Approved!' :
                           finalDecision.status === 'manual_review' ? 'Manual Review Required' :
                           finalDecision.status === 'conditional' ? 'Conditional Approval' :
                           'Application Decision Ready'}
                        </span>
                      </h3>
                      {/* Dynamic description based on decision status */}
                      <p className="text-gray-600 text-lg">
                        {finalDecision.status === 'approved'
                          ? 'Your loan has been approved. View your results below!'
                          : finalDecision.status === 'manual_review'
                          ? 'Your application requires additional review. See details below.'
                          : finalDecision.status === 'conditional'
                          ? 'Your loan is conditionally approved. View conditions below.'
                          : 'Your application has been processed. View details below.'}
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        // Ensure decision is in sessionStorage before navigating
                        if (finalDecision) {
                          sessionStorage.setItem('loanDecision', JSON.stringify(finalDecision));
                          window.location.href = '/results';
                        }
                      }}
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