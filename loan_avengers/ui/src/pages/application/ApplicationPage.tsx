import { useState } from 'react';
import { Layout } from '../../components/layout/Layout';
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
        <div className="py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center animate-fade-in">
              <div className="text-6xl mb-6" aria-hidden="true">🎭</div>
              
              <h1 className="text-4xl font-bold text-gray-900 mb-6">
                Hi! I'm Riley, Your Loan Orchestrator
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                I'm here to guide you through a revolutionary loan experience. 
                Instead of filling out boring forms, we'll have a natural conversation 
                where my AI specialist team will help you every step of the way.
              </p>

              <div className="card max-w-2xl mx-auto mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  Here's How It Works:
                </h2>
                
                <div className="space-y-4 text-left">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl" aria-hidden="true">💬</div>
                    <div>
                      <h3 className="font-medium text-gray-900">Natural Conversation</h3>
                      <p className="text-gray-600">Just chat with me like you would with a friend</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl" aria-hidden="true">🤝</div>
                    <div>
                      <h3 className="font-medium text-gray-900">Meet the Specialists</h3>
                      <p className="text-gray-600">I'll introduce you to Sarah, Marcus, and Alex as needed</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl" aria-hidden="true">⚡</div>
                    <div>
                      <h3 className="font-medium text-gray-900">Real-time Processing</h3>
                      <p className="text-gray-600">Watch as your loan gets processed in real-time</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl" aria-hidden="true">🎉</div>
                    <div>
                      <h3 className="font-medium text-gray-900">Celebrate Together</h3>
                      <p className="text-gray-600">We'll celebrate your approval as a team!</p>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={handleStartApplication}
                className="btn-primary text-lg px-8 py-4"
              >
                Let's Start Our Conversation!
              </button>
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
                    <div className="text-2xl" aria-hidden="true">🎭</div>
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
                    <div className="text-2xl" aria-hidden="true">🎭</div>
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
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Quick Application Form (Temporary)
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      className="input-field"
                      placeholder="Enter your full name"
                      onChange={(e) => setApplication({ ...application, applicantName: e.target.value })}
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      className="input-field"
                      placeholder="Enter your email"
                      onChange={(e) => setApplication({ ...application, email: e.target.value })}
                    />
                  </div>

                  <div>
                    <label htmlFor="loanAmount" className="block text-sm font-medium text-gray-700 mb-1">
                      Loan Amount
                    </label>
                    <input
                      type="number"
                      id="loanAmount"
                      name="loanAmount"
                      className="input-field"
                      placeholder="Enter desired loan amount"
                      onChange={(e) => setApplication({ ...application, loanAmount: parseInt(e.target.value) })}
                    />
                  </div>

                  <div>
                    <label htmlFor="loanPurpose" className="block text-sm font-medium text-gray-700 mb-1">
                      Loan Purpose
                    </label>
                    <select
                      id="loanPurpose"
                      name="loanPurpose"
                      className="input-field"
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
                    className="btn-primary w-full"
                    disabled={!application.applicantName || !application.email || !application.loanAmount}
                  >
                    Submit Application
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
        <div className="py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center animate-fade-in">
              <div className="text-6xl mb-6 animate-bounce-gentle" aria-hidden="true">⚡</div>
              
              <h1 className="text-4xl font-bold text-gray-900 mb-6">
                Your AI Team is Working Their Magic!
              </h1>
              
              <p className="text-xl text-gray-600 mb-8">
                Please wait while we process your application. This should only take a few moments.
              </p>

              <div className="card max-w-2xl mx-auto">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                  Processing Status
                </h2>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl" aria-hidden="true">💼</div>
                    <div className="flex-1 text-left">
                      <div className="text-gray-900 font-medium">Sarah - Credit Analysis</div>
                      <div className="text-green-600 text-sm">✓ Complete</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl" aria-hidden="true">📊</div>
                    <div className="flex-1 text-left">
                      <div className="text-gray-900 font-medium">Marcus - Income Verification</div>
                      <div className="text-blue-600 text-sm">⏳ In Progress...</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl" aria-hidden="true">🛡️</div>
                    <div className="flex-1 text-left">
                      <div className="text-gray-900 font-medium">Alex - Risk Assessment</div>
                      <div className="text-gray-500 text-sm">⏸️ Waiting...</div>
                    </div>
                  </div>
                </div>

                <div className="mt-8">
                  <div className="bg-gray-200 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full w-1/3 transition-all duration-1000"></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">33% Complete</p>
                </div>
              </div>

              <button
                onClick={() => window.location.href = '/results'}
                className="btn-primary mt-8"
              >
                View Results (Demo)
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return null;
}