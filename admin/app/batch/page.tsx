'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import type { GenerateRequest, BatchRequest, BatchJobStatus } from '@/lib/types';
import Link from 'next/link';
import { Heading } from '@/components/heading';
import { Button } from '@/components/button';
import { Divider } from '@/components/divider';
import { Input } from '@/components/input';
import { Textarea } from '@/components/textarea';
import { Select } from '@/components/select';
import { Field, Label } from '@/components/fieldset';
import { Text } from '@/components/text';
import { Badge } from '@/components/badge';

type InputMode = 'simple' | 'json';

export default function BatchPage() {
  const [mode, setMode] = useState<InputMode>('simple');

  // Simple mode state
  const [prompts, setPrompts] = useState('');
  const [experimentId, setExperimentId] = useState(`batch_${Date.now()}`);
  const [selectedModel, setSelectedModel] = useState('');
  const [stage, setStage] = useState('test');
  const [negativePrompt, setNegativePrompt] = useState('blurry, low quality, distorted, bad anatomy');
  const [steps, setSteps] = useState(20);
  const [cfgScale, setCfgScale] = useState(7);
  const [width, setWidth] = useState(1024);
  const [height, setHeight] = useState(1024);
  const [seed, setSeed] = useState(-1);
  const [denoise, setDenoise] = useState(1.0);
  const [scheduler, setScheduler] = useState('');

  // JSON mode state
  const [jsonInput, setJsonInput] = useState('');
  const [jsonError, setJsonError] = useState('');

  // Batch status polling
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null);

  // Fetch models
  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: () => apiClient.listModels(),
  });

  // Poll batch status
  const { data: batchStatus } = useQuery({
    queryKey: ['batch', activeBatchId],
    queryFn: () => apiClient.getBatchStatus(activeBatchId!),
    enabled: !!activeBatchId,
    refetchInterval: (data) => {
      if (!data) return 2000;
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
        return false; // Stop polling
      }
      return 2000; // Poll every 2 seconds
    },
  });

  // Set default model when loaded
  useState(() => {
    if (modelsData?.defaults?.model && !selectedModel) {
      setSelectedModel(modelsData.defaults.model);
    }
  });

  const createBatch = useMutation({
    mutationFn: (request: BatchRequest) => apiClient.createBatch(request),
    onSuccess: (response) => {
      setActiveBatchId(response.batch_id);
    },
  });

  const handleSubmit = () => {
    if (mode === 'simple') {
      // Build requests from simple input
      const promptLines = prompts.split('\n').filter(p => p.trim().length > 0);

      if (promptLines.length === 0) {
        alert('Please enter at least one prompt');
        return;
      }

      if (!selectedModel) {
        alert('Please select a model');
        return;
      }

      const requests: GenerateRequest[] = promptLines.map((prompt, index) => ({
        experiment_id: experimentId,
        stage,
        prompt: prompt.trim(),
        negative_prompt: negativePrompt || undefined,
        model: selectedModel,
        steps,
        cfg_scale: cfgScale,
        width,
        height,
        seed: seed === -1 ? Math.floor(Math.random() * 999999999) : seed + index,
        extra: {
          denoise: denoise < 1.0 ? denoise : undefined,
          scheduler: scheduler || undefined,
        },
      }));

      createBatch.mutate({
        experiment_id: experimentId,
        experiments: requests,
      });
    } else {
      // Parse JSON input
      try {
        const parsed = JSON.parse(jsonInput);

        // Support both array format and full BatchRequest format
        let requests: GenerateRequest[];
        let expId: string;

        if (Array.isArray(parsed)) {
          requests = parsed;
          expId = `batch_${Date.now()}`;
        } else if (parsed.experiments && Array.isArray(parsed.experiments)) {
          requests = parsed.experiments;
          expId = parsed.experiment_id || `batch_${Date.now()}`;
        } else {
          throw new Error('JSON must be an array of requests or a BatchRequest object');
        }

        if (requests.length === 0) {
          throw new Error('No requests in JSON');
        }

        // Get defaults from modelsData
        const defaults = modelsData?.defaults || {
          model: 'juggernaut_xl',
          steps: 25,
          cfg_scale: 7.0,
          width: 1024,
          height: 1024,
          scheduler: 'DPM++ 2M Karras'
        };

        // Apply defaults to each request
        const normalizedRequests: GenerateRequest[] = requests.map((req, index) => {
          // Ensure prompt exists
          if (!req.prompt) {
            throw new Error(`Request at index ${index} is missing 'prompt' field`);
          }

          // Build extra params - only include defined values
          const extra: any = {};
          if (req.extra?.denoise !== undefined) {
            extra.denoise = req.extra.denoise;
          }
          const schedulerValue = req.extra?.scheduler || (req as any).scheduler || defaults.scheduler;
          if (schedulerValue) {
            extra.scheduler = schedulerValue;
          }

          return {
            experiment_id: expId,
            stage: req.stage || 'batch',
            prompt: req.prompt,
            negative_prompt: req.negative_prompt || 'blurry, low quality, distorted, bad anatomy',
            model: req.model || defaults.model,
            steps: req.steps !== undefined ? req.steps : defaults.steps,
            cfg_scale: req.cfg_scale !== undefined ? req.cfg_scale : defaults.cfg_scale,
            width: req.width !== undefined ? req.width : defaults.width,
            height: req.height !== undefined ? req.height : defaults.height,
            seed: req.seed !== undefined ? req.seed : -1,
            ...(Object.keys(extra).length > 0 ? { extra } : {}),
          };
        });

        setJsonError('');
        setActiveBatchId(null); // Reset previous batch
        createBatch.mutate({
          experiment_id: expId,
          experiments: normalizedRequests,
        });
      } catch (error) {
        setJsonError(error instanceof Error ? error.message : 'Invalid JSON');
      }
    }
  };

  const enabledModels = modelsData?.models.filter(m => m.enabled) || [];
  const promptCount = prompts.split('\n').filter(p => p.trim()).length;

  return (
    <div>
      <Heading>Batch Generator</Heading>
      <Text>Generate multiple images at once with different prompts</Text>
      <Divider className="my-10 mt-6" />

      <div className="grid grid-cols-1 gap-x-8 gap-y-8 lg:grid-cols-2">
        {/* Input Section */}
        <div>
          <Heading level={2}>Configuration</Heading>
          <Divider className="my-4" soft />

          <div className="space-y-6">
            {/* Mode Toggle */}
            <Field>
              <Label>Input Mode</Label>
              <div className="flex gap-2 mt-2">
                <Button
                  onClick={() => setMode('simple')}
                  color={mode === 'simple' ? 'blue' : 'zinc'}
                  outline={mode !== 'simple'}
                >
                  Simple Mode
                </Button>
                <Button
                  onClick={() => setMode('json')}
                  color={mode === 'json' ? 'blue' : 'zinc'}
                  outline={mode !== 'json'}
                >
                  JSON Mode
                </Button>
              </div>
            </Field>

            {mode === 'simple' ? (
              <>
                {/* Simple Mode */}
                <Field>
                  <Label>Experiment ID</Label>
                  <Input
                    type="text"
                    value={experimentId}
                    onChange={(e) => setExperimentId(e.target.value)}
                  />
                </Field>

                <Field>
                  <Label>Prompts (one per line)</Label>
                  <Textarea
                    value={prompts}
                    onChange={(e) => setPrompts(e.target.value)}
                    rows={8}
                    placeholder="portrait of a woman, studio lighting&#10;landscape with mountains, sunset&#10;futuristic cityscape, neon lights"
                    className="font-mono text-sm"
                  />
                  <Text className="mt-1">{promptCount} prompts</Text>
                </Field>

                <Field>
                  <Label>Model *</Label>
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    <option value="">Select a model...</option>
                    {enabledModels.map((model) => (
                      <option key={model.alias} value={model.alias}>
                        {model.alias} - {model.description}
                      </option>
                    ))}
                  </Select>
                </Field>

                <div className="grid grid-cols-2 gap-4">
                  <Field>
                    <Label>Stage</Label>
                    <Input
                      type="text"
                      value={stage}
                      onChange={(e) => setStage(e.target.value)}
                    />
                  </Field>

                  <Field>
                    <Label>Steps</Label>
                    <Input
                      type="number"
                      value={steps}
                      onChange={(e) => setSteps(parseInt(e.target.value))}
                      min={1}
                      max={150}
                    />
                  </Field>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Field>
                    <Label>CFG Scale</Label>
                    <Input
                      type="number"
                      value={cfgScale}
                      onChange={(e) => setCfgScale(parseFloat(e.target.value))}
                      min={1}
                      max={20}
                      step={0.1}
                    />
                  </Field>

                  <Field>
                    <Label>Seed (-1 = random)</Label>
                    <Input
                      type="number"
                      value={seed}
                      onChange={(e) => setSeed(parseInt(e.target.value))}
                    />
                  </Field>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Field>
                    <Label>Width</Label>
                    <Input
                      type="number"
                      value={width}
                      onChange={(e) => setWidth(parseInt(e.target.value))}
                      step={64}
                    />
                  </Field>

                  <Field>
                    <Label>Height</Label>
                    <Input
                      type="number"
                      value={height}
                      onChange={(e) => setHeight(parseInt(e.target.value))}
                      step={64}
                    />
                  </Field>
                </div>

                <Field>
                  <Label>Negative Prompt</Label>
                  <Textarea
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    rows={3}
                  />
                </Field>

                <div className="grid grid-cols-2 gap-4">
                  <Field>
                    <Label>Denoise (1.0 = full)</Label>
                    <Input
                      type="number"
                      value={denoise}
                      onChange={(e) => setDenoise(parseFloat(e.target.value))}
                      min={0}
                      max={1}
                      step={0.05}
                    />
                  </Field>

                  <Field>
                    <Label>Scheduler (optional)</Label>
                    <Input
                      type="text"
                      value={scheduler}
                      onChange={(e) => setScheduler(e.target.value)}
                      placeholder="e.g. karras"
                    />
                  </Field>
                </div>
              </>
            ) : (
              <>
                {/* JSON Mode */}
                <Field>
                  <Label>Paste JSON Config</Label>
                  <Textarea
                    value={jsonInput}
                    onChange={(e) => {
                      setJsonInput(e.target.value);
                      setJsonError('');
                    }}
                    rows={20}
                    placeholder={`[\n  {\n    "prompt": "A beautiful sunset over mountains"\n  },\n  {\n    "prompt": "Portrait of a woman, professional photography",\n    "steps": 30,\n    "cfg_scale": 7.5\n  },\n  {\n    "prompt": "Cyberpunk city at night",\n    "model": "flux_fast",\n    "steps": 4\n  }\n]\n\nNote: Only 'prompt' is required!\nDefaults: juggernaut_xl, 25 steps, 1024x1024`}
                    className="font-mono text-sm"
                  />
                  {jsonError && (
                    <Text className="mt-2 text-red-600 dark:text-red-400">{jsonError}</Text>
                  )}
                  <div className="mt-3 space-y-2">
                    <Text className="font-medium">Format:</Text>
                    <ul className="text-sm space-y-1 list-disc list-inside text-zinc-600 dark:text-zinc-400">
                      <li>Only <code className="px-1 py-0.5 bg-zinc-100 dark:bg-zinc-800 rounded">prompt</code> field is required</li>
                      <li>experiment_id is auto-generated (batch_[timestamp])</li>
                      <li>Default model: <strong>juggernaut_xl</strong></li>
                      <li>See configs/example_batch_config.json for more examples</li>
                    </ul>
                  </div>
                </Field>
              </>
            )}

            {/* Submit Button */}
            <div className="pt-4">
              <Button
                onClick={handleSubmit}
                disabled={createBatch.isPending}
                className="w-full"
                color="green"
              >
                {createBatch.isPending ? 'Creating Batch...' : 'Start Batch Generation'}
              </Button>
              {createBatch.error && (
                <Text className="mt-2 text-red-600 dark:text-red-400">
                  Error: {createBatch.error instanceof Error ? createBatch.error.message : 'Unknown error'}
                </Text>
              )}
            </div>
          </div>
        </div>

        {/* Status Section */}
        <div>
          <Heading level={2}>Batch Status</Heading>
          <Divider className="my-4" soft />

          {activeBatchId && batchStatus ? (
            <div className="space-y-6">
              {/* Overall Progress */}
              <div>
                <div className="flex justify-between text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  <Text>Overall Progress</Text>
                  <Text>
                    {batchStatus.completed + batchStatus.failed} / {batchStatus.total}
                  </Text>
                </div>
                <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${((batchStatus.completed + batchStatus.failed) / batchStatus.total) * 100}%`,
                    }}
                  />
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {batchStatus.completed}
                  </div>
                  <Text className="text-xs">Completed</Text>
                </div>
                <div className="bg-red-50 dark:bg-red-950 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {batchStatus.failed}
                  </div>
                  <Text className="text-xs">Failed</Text>
                </div>
                <div className="bg-zinc-50 dark:bg-zinc-900 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-zinc-600 dark:text-zinc-400">
                    {batchStatus.total - batchStatus.completed - batchStatus.failed}
                  </div>
                  <Text className="text-xs">Pending</Text>
                </div>
              </div>

              {/* Status Badge */}
              <div className="flex items-center justify-between">
                <Text>Status:</Text>
                <Badge
                  color={
                    batchStatus.status === 'completed'
                      ? 'green'
                      : batchStatus.status === 'failed'
                      ? 'red'
                      : batchStatus.status === 'processing'
                      ? 'blue'
                      : 'zinc'
                  }
                >
                  {batchStatus.status}
                </Badge>
              </div>

              {/* Individual Items */}
              <div>
                <Divider soft />
                <div className="mt-4">
                  <Text className="font-medium mb-3">Individual Jobs</Text>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {batchStatus.items.map((item, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 rounded-lg border border-zinc-950/10 dark:border-white/10"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Text className="font-medium">Job {index + 1}</Text>
                            <Badge
                              color={
                                item.status === 'completed'
                                  ? 'green'
                                  : item.status === 'failed'
                                  ? 'red'
                                  : item.status === 'processing'
                                  ? 'blue'
                                  : 'zinc'
                              }
                            >
                              {item.status}
                            </Badge>
                          </div>

                          {/* Progress bar for processing items */}
                          {item.status === 'processing' && item.progress !== undefined && item.progress > 0 && (
                            <div className="mt-2">
                              <div className="flex justify-between text-xs text-zinc-600 dark:text-zinc-400 mb-1">
                                <Text>Generating...</Text>
                                <Text>{Math.round(item.progress * 100)}%</Text>
                              </div>
                              <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-1.5">
                                <div
                                  className="bg-blue-600 dark:bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                                  style={{ width: `${item.progress * 100}%` }}
                                />
                              </div>
                            </div>
                          )}

                          {item.error && (
                            <Text className="text-xs text-red-600 dark:text-red-400 mt-1">{item.error}</Text>
                          )}
                        </div>
                        {item.result && (
                          <Button
                            href={`/gallery?experiment=${batchStatus.experiment_id}`}
                            outline
                          >
                            View
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Actions */}
              {batchStatus.status === 'completed' && (
                <div>
                  <Divider soft />
                  <div className="mt-4">
                    <Button
                      href={`/gallery?experiment=${batchStatus.experiment_id}`}
                      className="w-full"
                    >
                      View All Results in Gallery
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Text className="text-zinc-500 dark:text-zinc-400">
                No active batch. Start a batch generation to see progress here.
              </Text>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
