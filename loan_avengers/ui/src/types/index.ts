// Core application types for the Loan Avengers frontend
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  specialty: string;
  avatar?: string;
  status: 'idle' | 'working' | 'complete' | 'error';
}

export interface LoanApplication {
  id?: string;
  applicantName: string;
  email: string;
  phone: string;
  loanAmount: number;
  loanPurpose: 'home_purchase' | 'refinance' | 'investment';
  creditScore?: number;
  annualIncome?: number;
  employmentStatus: 'employed' | 'self_employed' | 'unemployed' | 'retired';
  employmentLength?: number;
  status: 'draft' | 'submitted' | 'processing' | 'approved' | 'rejected';
  createdAt?: string;
  updatedAt?: string;
}

export interface ProcessingStep {
  id: string;
  name: string;
  description: string;
  agent: Agent;
  status: 'pending' | 'in_progress' | 'complete' | 'error';
  progress: number;
  startTime?: string;
  endTime?: string;
  message?: string;
}

export interface LoanDecision {
  applicationId: string;
  status: 'approved' | 'rejected' | 'conditional';
  loanAmount: number;
  interestRate: number;
  monthlyPayment: number;
  term: number;
  conditions?: string[];
  reasoning: string;
  nextSteps: string[];
  agentAssessments: Record<string, unknown>;
}

export interface RouteInfo {
  path: string;
  title: string;
  description?: string;
  requiresAuth?: boolean;
}

export interface ErrorInfo {
  code: string;
  message: string;
  details?: string;
  recoverable: boolean;
  retryAction?: () => void;
}

export interface AccessibilityConfig {
  screenReaderEnabled: boolean;
  highContrast: boolean;
  fontSize: 'small' | 'medium' | 'large';
  reduceMotion: boolean;
}