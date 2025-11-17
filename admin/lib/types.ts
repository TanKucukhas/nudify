/**
 * TypeScript types matching the backend API models
 */

export interface ExtraParams {
  denoise?: number;
  scheduler?: string;
  clip_skip?: number;
  [key: string]: any;
}

export interface GenerateRequest {
  experiment_id: string;
  stage: string;
  prompt: string;
  negative_prompt?: string;
  seed?: number;
  width?: number;
  height?: number;
  steps?: number;
  cfg_scale?: number;
  model: string;
  input_image?: string;
  extra?: ExtraParams;
}

export interface ImageMetadata {
  seed: number;
  model: string;
  steps: number;
  cfg_scale: number;
  width: number;
  height: number;
  denoise?: number;
  scheduler?: string;
}

export interface GenerateResponse {
  ok: boolean;
  experiment_id: string;
  stage: string;
  image_path: string;
  metadata: ImageMetadata;
  error?: string;
}

export interface ModelConfig {
  alias: string;
  checkpoint_file: string;
  type: string;
  description: string;
  enabled: boolean;
  recommended_settings?: {
    width: number;
    height: number;
    steps: number;
    cfg_scale: number;
    scheduler: string;
  };
}

export interface ModelsResponse {
  models: ModelConfig[];
  defaults: {
    model: string;
    fallback_model: string;
    width: number;
    height: number;
    steps: number;
    cfg_scale: number;
    scheduler: string;
  };
  scheduler_aliases: Record<string, string>;
}

export interface ExperimentSummary {
  experiment_id: string;
  created_at: number;
  image_count: number;
  stages: string[];
  has_results: boolean;
  latest_image: string | null;
}

export interface ImageInfo {
  filename: string;
  path: string;
  size_bytes: number;
  created_at: number;
}

export interface ExperimentDetail {
  experiment_id: string;
  images: ImageInfo[];
  results: GenerateResponse[];
  stats: {
    total_images: number;
    successful: number;
    failed: number;
  };
}

export interface BatchRequest {
  experiment_id: string;
  experiments: GenerateRequest[];
}

export interface BatchJobItem {
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  result?: GenerateResponse;
  error?: string;
  started_at?: string;
  completed_at?: string;
}

export interface BatchJobStatus {
  batch_id: string;
  experiment_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  total: number;
  completed: number;
  failed: number;
  current_item?: number;
  items: BatchJobItem[];
}

export interface BatchCreateResponse {
  batch_id: string;
  status: string;
  total: number;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  comfyui: 'connected' | 'disconnected';
  comfyui_url: string;
}
