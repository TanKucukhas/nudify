/**
 * API Client for communicating with the backend
 */
import axios, { AxiosInstance } from 'axios';
import type {
  GenerateRequest,
  GenerateResponse,
  ModelsResponse,
  ExperimentSummary,
  ExperimentDetail,
  BatchRequest,
  BatchJobStatus,
  BatchCreateResponse,
  HealthResponse,
} from './types';

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health Check
  async health(): Promise<HealthResponse> {
    const { data } = await this.client.get<HealthResponse>('/health');
    return data;
  }

  // Models
  async listModels(): Promise<ModelsResponse> {
    const { data } = await this.client.get<ModelsResponse>('/api/models');
    return data;
  }

  // Experiments
  async listExperiments(): Promise<{ experiments: ExperimentSummary[] }> {
    const { data } = await this.client.get('/api/experiments');
    return data;
  }

  async getExperiment(experimentId: string): Promise<ExperimentDetail> {
    const { data} = await this.client.get<ExperimentDetail>(`/api/experiments/${experimentId}`);
    return data;
  }

  async deleteExperiment(experimentId: string): Promise<{ ok: boolean; message: string }> {
    const { data } = await this.client.delete(`/api/experiments/${experimentId}`);
    return data;
  }

  // Image URLs
  getImageUrl(experimentId: string, filename: string): string {
    return `${this.client.defaults.baseURL}/api/experiments/${experimentId}/images/${filename}`;
  }

  // Single Generation
  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    const { data } = await this.client.post<GenerateResponse>('/generate', request);
    return data;
  }

  // Batch Generation
  async createBatch(request: BatchRequest): Promise<BatchCreateResponse> {
    const { data } = await this.client.post<BatchCreateResponse>('/api/batch', request);
    return data;
  }

  async getBatchStatus(batchId: string): Promise<BatchJobStatus> {
    const { data } = await this.client.get<BatchJobStatus>(`/api/batch/${batchId}`);
    return data;
  }

  async listBatches(): Promise<{ jobs: any[] }> {
    const { data } = await this.client.get('/api/batch');
    return data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
