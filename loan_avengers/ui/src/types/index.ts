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

// Coordinator Chat Interface Types
export interface ChatMessage {
  id: string;
  sender: 'user' | 'coordinator';
  message: string;
  timestamp: Date;
  typing?: boolean;
}

export interface QuickReplyOption {
  label: string;
  value: string | number;
  icon?: string;
}

export interface CoordinatorResponse {
  agent_name: string;
  message: string;
  action: 'collect_info' | 'ready_for_processing' | 'need_clarification' | 'completed';
  collected_data: Record<string, any>;
  next_step: string;
  completion_percentage: number;
  quick_replies?: QuickReplyOption[];
}

export interface ChatSession {
  id: string;
  thread_id?: string;
  messages: ChatMessage[];
  collected_data: Record<string, any>;
  completion_percentage: number;
  status: 'active' | 'complete' | 'processing' | 'error';
  created_at: Date;
  updated_at: Date;
}