import { useState } from 'react';
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

  const handleStartApplication = () => {
    setCurrentStep('conversation');
  };

  const handleSubmitApplication = () => {
    setCurrentStep('processing');
    // TODO: Integrate with backend API
    console.log('Submitting application:', application);
  };

  const handleApplicationComplete = (applicationData: Record<string, any>) => {
    console.log('Application completed by Riley:', applicationData);
    // Convert Riley's collected data to LoanApplication format
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

    // Move to processing step
    setCurrentStep('processing');
  };

  const handleProgressUpdate = (percentage: number) => {
    setConversationProgress(percentage);
  };

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
                        Talk naturally - Riley understands conversational language
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

              <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
                Please wait while we process your application. This should only take a few moments.
              </p>

              {/* Workflow Progress */}
              <div className="card-elevated max-w-4xl mx-auto mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
                  Processing Workflow
                </h2>

                {/* Progress Steps */}
                <div className="relative">
                  {/* Progress Line */}
                  <div className="absolute top-8 left-0 right-0 h-0.5 bg-gray-200">
                    <div className="h-full bg-gradient-to-r from-brand-500 to-brand-600 rounded-full w-1/3 animate-progress"></div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
                    {/* Intake Agent - Completed */}
                    <div className="workflow-step completed animate-workflow-step">
                      <div className="flex flex-col items-center">
                        <div className="w-16 h-16 bg-gradient-to-br from-success-500 to-success-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-1">Intake</h3>
                        <p className="text-sm text-success-600 font-medium">Complete</p>
                        <p className="text-xs text-gray-500 mt-1 text-center">Application received and validated</p>
                      </div>
                    </div>

                    {/* Credit Agent - In Progress */}
                    <div className="workflow-step active animate-workflow-step" style={{animationDelay: '0.2s'}}>
                      <div className="flex flex-col items-center">
                        <div className="w-16 h-16 bg-gradient-to-br from-brand-500 to-brand-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg animate-pulse-soft">
                          <span className="text-2xl" aria-hidden="true">🦸‍♀️</span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-1">Credit Analysis</h3>
                        <p className="text-sm text-brand-600 font-medium">In Progress...</p>
                        <p className="text-xs text-gray-500 mt-1 text-center">Sarah is analyzing your credit profile</p>
                      </div>
                    </div>

                    {/* Income Agent - Pending */}
                    <div className="workflow-step pending animate-workflow-step" style={{animationDelay: '0.4s'}}>
                      <div className="flex flex-col items-center">
                        <div className="w-16 h-16 bg-gray-200 rounded-2xl flex items-center justify-center mb-4">
                          <span className="text-2xl opacity-50" aria-hidden="true">🦸</span>
                        </div>
                        <h3 className="font-medium text-gray-500 mb-1">Income Verification</h3>
                        <p className="text-sm text-gray-400 font-medium">Waiting...</p>
                        <p className="text-xs text-gray-400 mt-1 text-center">Marcus will verify your income</p>
                      </div>
                    </div>

                    {/* Risk Agent - Pending */}
                    <div className="workflow-step pending animate-workflow-step" style={{animationDelay: '0.6s'}}>
                      <div className="flex flex-col items-center">
                        <div className="w-16 h-16 bg-gray-200 rounded-2xl flex items-center justify-center mb-4">
                          <span className="text-2xl opacity-50" aria-hidden="true">🦹‍♂️</span>
                        </div>
                        <h3 className="font-medium text-gray-500 mb-1">Risk Assessment</h3>
                        <p className="text-sm text-gray-400 font-medium">Waiting...</p>
                        <p className="text-xs text-gray-400 mt-1 text-center">Alex will assess overall risk</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Overall Progress */}
                <div className="mt-10 pt-6 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                    <span className="text-sm font-medium text-brand-600">33% Complete</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{width: '33%'}}></div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => window.location.href = '/results'}
                className="btn-secondary px-8 py-3 shadow-lg hover:shadow-xl transition-all duration-300"
              >
                <span>View Results (Demo)</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return null;
}