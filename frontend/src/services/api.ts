/**
 * API service for communicating with the Legal Intel Dashboard backend
 */
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  DocumentResponse,
  UploadResponse,
  QueryRequest,
  QueryResponse,
  DashboardStats,
  DashboardSummary,
  RecentActivity,
  ApiError,
} from '../types/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NODE_ENV === 'production' 
        ? '/api/v1' 
        : 'http://localhost:8000/api/v1',
      timeout: 30000, // 30 seconds for large file uploads
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        
        // Transform error response
        const apiError: ApiError = {
          error: error.response?.data?.error || 'Network Error',
          message: error.response?.data?.message || error.message,
          details: error.response?.data?.details,
        };
        
        return Promise.reject(apiError);
      }
    );
  }

  /**
   * Upload multiple documents
   */
  async uploadDocuments(files: File[]): Promise<UploadResponse> {
    if (!files || files.length === 0) {
      throw new Error('No files provided for upload');
    }

    const formData = new FormData();
    
    // Append each file with the same field name 'files'
    files.forEach((file) => {
      formData.append('files', file, file.name);
    });

    console.log('Uploading files:', files.map(f => ({ name: f.name, size: f.size, type: f.type })));

    try {
      const response = await this.client.post<UploadResponse>('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes for uploads
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            console.log(`Upload progress: ${progress}%`);
          }
        }
      });

      console.log('Upload successful:', response.data);
      return response.data;
      
    } catch (error: any) {
      console.error('Upload failed:', error);
      
      if (error.response?.status === 422) {
        console.error('Validation error details:', error.response.data);
        throw new Error(`Upload validation failed: ${error.response.data?.detail || 'Invalid file format or data'}`);
      }
      
      throw error;
    }
  }

  /**
   * Query documents with natural language
   */
  async queryDocuments(question: string): Promise<QueryResponse> {
    const request: QueryRequest = { question };
    
    const response = await this.client.post<QueryResponse>('/query', request);
    return response.data;
  }

  /**
   * Get all documents
   */
  async getDocuments(skip = 0, limit = 100): Promise<DocumentResponse[]> {
    const response = await this.client.get<DocumentResponse[]>('/documents', {
      params: { skip, limit },
    });
    return response.data;
  }

  /**
   * Get specific document by ID
   */
  async getDocument(id: number): Promise<DocumentResponse> {
    const response = await this.client.get<DocumentResponse>(`/documents/${id}`);
    return response.data;
  }

  /**
   * Delete document
   */
  async deleteDocument(id: number): Promise<{ message: string }> {
    const response = await this.client.delete<{ message: string }>(`/documents/${id}`);
    return response.data;
  }

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get<DashboardStats>('/dashboard');
    return response.data;
  }

  /**
   * Get dashboard summary
   */
  async getDashboardSummary(): Promise<DashboardSummary> {
    const response = await this.client.get<DashboardSummary>('/dashboard/summary');
    return response.data;
  }

  /**
   * Get recent activity
   */
  async getRecentActivity(limit = 10): Promise<RecentActivity> {
    const response = await this.client.get<RecentActivity>('/dashboard/recent-activity', {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string; ai_enabled: boolean }> {
    // Use full URL for health check to avoid proxy issues
    const baseUrl = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';
    const response = await axios.get(`${baseUrl}/health`);
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export { ApiService };