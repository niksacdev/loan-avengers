import { useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { ExperimentalDisclaimer } from '../../components/ui/ExperimentalDisclaimer';
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

  const handleStartApplication = () => {
    setCurrentStep('conversation');
  };

  const handleSubmitApplication = () => {
    setCurrentStep('processing');
    // TODO: Integrate with backend API
    console.log('Submitting application:', application);
  };

  if (currentStep === 'intro') {
    return (
      <Layout title="Start Your Loan Application">
        <div className="animate-fade-in">
          {/* Experimental Disclaimer */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
            <ExperimentalDisclaimer />
          </div>

          <div className="py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center animate-fade-in-up">
              <div className="relative inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-brand-500 via-brand-600 to-accent-600 rounded-2xl shadow-xl shadow-brand-500/25 mb-8 animate-bounce-gentle">
                <span className="text-3xl" aria-hidden="true">🦸‍♂️</span>
                <div className="absolute -inset-1 bg-gradient-to-r from-brand-400 to-accent-500 rounded-2xl blur-sm opacity-25 animate-pulse"></div>
                <span className="absolute -top-1 -right-1 text-xs animate-ping delay-500">✨</span>
              </div>

              <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-dark-text-primary mb-6 tracking-tight transition-colors duration-300">
                Hi! I'm{' '}
                <span className="relative inline-block">
                  <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-accent-600 bg-clip-text text-transparent">
                    Riley
                  </span>
                  <span className="absolute -top-1 -right-2 text-lg animate-bounce delay-200">✨</span>
                </span>
                , Your Loan Orchestrator
              </h1>

              <p className="text-xl lg:text-2xl text-gray-600 dark:text-dark-text-secondary mb-10 max-w-3xl mx-auto leading-relaxed transition-colors duration-300">
                I'm here to guide you through a revolutionary loan experience.
                Instead of filling out boring forms, we'll have a natural conversation
                where my AI specialist team will help you every step of the way.
              </p>

              <div className="card-elevated max-w-3xl mx-auto mb-10 dark:bg-dark-bg-card transition-colors duration-300">
                <h2 className="text-2xl lg:text-3xl font-semibold text-gray-900 dark:text-dark-text-primary mb-8 text-center transition-colors duration-300">
                  Here's How It Works:
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-start space-x-4 p-4 rounded-xl bg-brand-50 dark:bg-dark-bg-tertiary border border-brand-200 dark:border-dark-bg-tertiary group hover:scale-[1.02] transition-all duration-300">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-brand-400 to-brand-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-xl text-white" aria-hidden="true">💬</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors duration-300">Natural Conversation</h3>
                      <p className="text-gray-600 dark:text-dark-text-secondary text-sm leading-relaxed transition-colors duration-300">Just chat with me like you would with a friend</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4 p-4 rounded-xl bg-primary-50 dark:bg-dark-bg-tertiary border border-primary-200 dark:border-dark-bg-tertiary group hover:scale-[1.02] transition-all duration-300">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-xl text-white" aria-hidden="true">🤝</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors duration-300">Meet the Specialists</h3>
                      <p className="text-gray-600 dark:text-dark-text-secondary text-sm leading-relaxed transition-colors duration-300">I'll introduce you to Sarah, Marcus, and Alex as needed</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4 p-4 rounded-xl bg-warning-50 dark:bg-dark-bg-tertiary border border-warning-200 dark:border-dark-bg-tertiary group hover:scale-[1.02] transition-all duration-300">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-warning-400 to-warning-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-xl text-white" aria-hidden="true">⚡</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors duration-300">Real-time Processing</h3>
                      <p className="text-gray-600 dark:text-dark-text-secondary text-sm leading-relaxed transition-colors duration-300">Watch as your loan gets processed in real-time</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4 p-4 rounded-xl bg-success-50 dark:bg-dark-bg-tertiary border border-success-200 dark:border-dark-bg-tertiary group hover:scale-[1.02] transition-all duration-300">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-success-400 to-success-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-xl text-white" aria-hidden="true">🎉</span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-dark-text-primary mb-2 transition-colors duration-300">Celebrate Together</h3>
                      <p className="text-gray-600 dark:text-dark-text-secondary text-sm leading-relaxed transition-colors duration-300">We'll celebrate your approval as a team!</p>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={handleStartApplication}
                className="btn-primary text-lg px-10 py-5 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 group"
              >
                <span>Let's Start Our Conversation!</span>
                <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (currentStep === 'conversation') {
    return (
      <Layout title="Chat with Your AI Team">
        <div className="py-8">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Conversation UI Placeholder */}
            <div className="card animate-fade-in">
              <div className="text-center mb-8">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Conversational Interface Coming Soon!
                </h1>
                <p className="text-gray-600">
                  This is where you'll have natural conversations with Riley and the AI team.
                </p>
              </div>

              {/* Placeholder for conversation interface */}
              <div className="bg-gray-50 rounded-lg p-8 mb-6">
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl" aria-hidden="true">🦸‍♂️</div>
                    <div className="bg-white rounded-lg p-3 flex-1">
                      <p className="text-gray-900">
                        <strong>Riley:</strong> Hi! I'm excited to help you with your loan. 
                        What type of loan are you looking for today?
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3 justify-end">
                    <div className="bg-primary-600 text-white rounded-lg p-3 max-w-xs">
                      <p>I'm looking to buy my first home!</p>
                    </div>
                    <div className="text-2xl" aria-hidden="true">😊</div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="text-2xl" aria-hidden="true">🦸‍♂️</div>
                    <div className="bg-white rounded-lg p-3 flex-1">
                      <p className="text-gray-900">
                        <strong>Riley:</strong> That's fantastic! First-time homebuying is such an exciting journey. 
                        Let me introduce you to Sarah, our credit specialist, who can help us understand 
                        your financial picture...
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Temporary form for demo purposes */}
              <div className="border-t border-gray-200 pt-8 mt-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">
                  Quick Application Form (Temporary)
                </h3>

                <div className="max-w-lg mx-auto space-y-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-semibold text-gray-800 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      className="input-field-lg"
                      placeholder="Enter your full name"
                      onChange={(e) => setApplication({ ...application, applicantName: e.target.value })}
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-gray-800 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      className="input-field-lg"
                      placeholder="Enter your email address"
                      onChange={(e) => setApplication({ ...application, email: e.target.value })}
                    />
                  </div>

                  <div>
                    <label htmlFor="loanAmount" className="block text-sm font-semibold text-gray-800 mb-2">
                      Loan Amount
                    </label>
                    <div className="relative">
                      <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 text-lg">$</span>
                      <input
                        type="number"
                        id="loanAmount"
                        name="loanAmount"
                        className="input-field-lg pl-8"
                        placeholder="Enter desired loan amount"
                        onChange={(e) => setApplication({ ...application, loanAmount: parseInt(e.target.value) })}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="loanPurpose" className="block text-sm font-semibold text-gray-800 mb-2">
                      Loan Purpose
                    </label>
                    <select
                      id="loanPurpose"
                      name="loanPurpose"
                      className="input-field-lg"
                      onChange={(e) => setApplication({ ...application, loanPurpose: e.target.value as LoanApplication['loanPurpose'] })}
                    >
                      <option value="">Select loan purpose</option>
                      <option value="home_purchase">Home Purchase</option>
                      <option value="refinance">Refinance</option>
                      <option value="investment">Investment Property</option>
                    </select>
                  </div>

                  <button
                    onClick={handleSubmitApplication}
                    className="btn-primary w-full text-lg px-8 py-4 shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-300 group"
                    disabled={!application.applicantName || !application.email || !application.loanAmount}
                  >
                    <span>Submit Application</span>
                    <svg className="w-6 h-6 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </button>
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