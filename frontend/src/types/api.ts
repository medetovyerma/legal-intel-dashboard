/**
 * TypeScript interfaces for API communication
 */

export interface DocumentResponse {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_error?: string;
  agreement_type?: string;
  governing_law?: string;
  jurisdiction?: string;
  geography?: string;
  industry_sector?: string;
  confidence_score?: number;
  created_at: string;
  updated_at?: string;
}

export interface UploadResponse {
  message: string;
  uploaded_files: DocumentResponse[];
  failed_files: Array<{
    filename: string;
    error: string;
  }>;
}

export interface QueryRequest {
  question: string;
}

export interface QueryResult {
  document: string;
  data: Record<string, any>;
}

export interface QueryResponse {
  question: string;
  results: QueryResult[];
  total_matches: number;
}

export interface DashboardStats {
  agreement_types: Record<string, number>;
  jurisdictions: Record<string, number>;
  industries: Record<string, number>;
  total_documents: number;
  processing_status: Record<string, number>;
}

export interface DashboardSummary {
  total_documents: number;
  completed_documents: number;
  pending_documents: number;
  processing_documents: number;
  failed_documents: number;
  completion_rate: number;
  unique_agreement_types: number;
  unique_jurisdictions: number;
  unique_industries: number;
}

export interface RecentActivity {
  recent_activity: Array<{
    id: number;
    filename: string;
    status: string;
    agreement_type?: string;
    created_at: string;
    updated_at?: string;
  }>;
}

// API Error response
export interface ApiError {
  error: string;
  message: string;
  details?: any;
}