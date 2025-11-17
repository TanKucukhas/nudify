'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import type { GenerateRequest, GenerateResponse } from '@/lib/types';
import Image from 'next/image';
import { Heading } from '@/components/heading';
import { Button } from '@/components/button';
import { Divider } from '@/components/divider';
import { Input } from '@/components/input';
import { Textarea } from '@/components/textarea';
import { Select } from '@/components/select';
import { Field, Label } from '@/components/fieldset';
import { Text } from '@/components/text';
import { Badge } from '@/components/badge';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('blurry, low quality, distorted, bad anatomy');
  const [experimentId, setExperimentId] = useState(`test_${Date.now()}`);
  const [stage, setStage] = useState('test');
  const [selectedModel, setSelectedModel] = useState('');
  const [steps, setSteps] = useState(20);
  const [cfgScale, setCfgScale] = useState(7);
  const [width, setWidth] = useState(1024);
  const [height, setHeight] = useState(1024);
  const [seed, setSeed] = useState(-1);
  const [denoise, setDenoise] = useState(1.0);
  const [scheduler, setScheduler] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [generatedImage, setGeneratedImage] = useState<GenerateResponse | null>(null);

  const { data: modelsData, isLoading: modelsLoading } = useQuery({
    queryKey: ['models'],
    queryFn: () => apiClient.listModels(),
  });

  useEffect(() => {
    if (modelsData && !selectedModel) {
      const defaultModel = modelsData.defaults?.model || modelsData.models.find(m => m.enabled)?.alias;
      if (defaultModel) {
        setSelectedModel(defaultModel);
        const model = modelsData.models.find(m => m.alias === defaultModel);
        if (model?.recommended_settings) {
          setSteps(model.recommended_settings.steps);
          setCfgScale(model.recommended_settings.cfg_scale);
          setWidth(model.recommended_settings.width);
          setHeight(model.recommended_settings.height);
          setScheduler(model.recommended_settings.scheduler || '');
        }
      }
    }
  }, [modelsData, selectedModel]);

  const handleModelChange = (modelAlias: string) => {
    setSelectedModel(modelAlias);
    const model = modelsData?.models.find(m => m.alias === modelAlias);
    if (model?.recommended_settings) {
      setSteps(model.recommended_settings.steps);
      setCfgScale(model.recommended_settings.cfg_scale);
      setWidth(model.recommended_settings.width);
      setHeight(model.recommended_settings.height);
      setScheduler(model.recommended_settings.scheduler || '');
    }
  };

  const generateMutation = useMutation({
    mutationFn: (request: GenerateRequest) => apiClient.generate(request),
    onSuccess: (response) => {
      setGeneratedImage(response);
      setExperimentId(`test_${Date.now()}`);
    },
  });

  const handleGenerate = () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    if (!selectedModel) {
      alert('Please select a model');
      return;
    }

    const request: GenerateRequest = {
      experiment_id: experimentId,
      stage,
      prompt: prompt.trim(),
      negative_prompt: negativePrompt || undefined,
      model: selectedModel,
      steps,
      cfg_scale: cfgScale,
      width,
      height,
      seed: seed === -1 ? Math.floor(Math.random() * 999999999) : seed,
      extra: {
        denoise: denoise < 1.0 ? denoise : undefined,
        scheduler: scheduler || undefined,
      },
    };

    generateMutation.mutate(request);
  };

  const enabledModels = modelsData?.models.filter(m => m.enabled) || [];

  return (
    <div>
      <Heading>Generate Image</Heading>
      <Text>Create a single image with custom parameters</Text>
      <Divider className="my-10 mt-6" />

      <div className="grid grid-cols-1 gap-x-8 gap-y-8 lg:grid-cols-2">
        {/* Parameters */}
        <div>
          <Heading level={2}>Parameters</Heading>
          <Divider className="my-4" soft />

          <div className="space-y-6">
            <Field>
              <Label>Prompt *</Label>
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                placeholder="Describe the image you want to generate..."
              />
            </Field>

            <Field>
              <Label>Negative Prompt</Label>
              <Textarea
                value={negativePrompt}
                onChange={(e) => setNegativePrompt(e.target.value)}
                rows={2}
                placeholder="What to avoid..."
              />
            </Field>

            <Field>
              <Label>Model *</Label>
              <Select
                value={selectedModel}
                onChange={(e) => handleModelChange(e.target.value)}
                disabled={modelsLoading}
              >
                {modelsLoading ? (
                  <option>Loading models...</option>
                ) : (
                  <>
                    <option value="">Select a model...</option>
                    {enabledModels.map((model) => (
                      <option key={model.alias} value={model.alias}>
                        {model.alias} - {model.description}
                      </option>
                    ))}
                  </>
                )}
              </Select>
              {selectedModel && (
                <Text className="mt-2">
                  {modelsData?.models.find(m => m.alias === selectedModel)?.type}
                </Text>
              )}
            </Field>

            <div className="grid grid-cols-2 gap-4">
              <Field>
                <Label>Experiment ID</Label>
                <Input
                  type="text"
                  value={experimentId}
                  onChange={(e) => setExperimentId(e.target.value)}
                />
              </Field>

              <Field>
                <Label>Stage</Label>
                <Input
                  type="text"
                  value={stage}
                  onChange={(e) => setStage(e.target.value)}
                />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Field>
                <Label>Steps: {steps}</Label>
                <input
                  type="range"
                  value={steps}
                  onChange={(e) => setSteps(parseInt(e.target.value))}
                  min={1}
                  max={150}
                  className="w-full"
                />
                <Input
                  type="number"
                  value={steps}
                  onChange={(e) => setSteps(parseInt(e.target.value))}
                  min={1}
                  max={150}
                  className="mt-2"
                />
              </Field>

              <Field>
                <Label>CFG Scale: {cfgScale}</Label>
                <input
                  type="range"
                  value={cfgScale}
                  onChange={(e) => setCfgScale(parseFloat(e.target.value))}
                  min={1}
                  max={20}
                  step={0.5}
                  className="w-full"
                />
                <Input
                  type="number"
                  value={cfgScale}
                  onChange={(e) => setCfgScale(parseFloat(e.target.value))}
                  min={1}
                  max={20}
                  step={0.1}
                  className="mt-2"
                />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Field>
                <Label>Width</Label>
                <Select
                  value={width}
                  onChange={(e) => setWidth(parseInt(e.target.value))}
                >
                  <option value={512}>512</option>
                  <option value={768}>768</option>
                  <option value={1024}>1024</option>
                  <option value={1280}>1280</option>
                  <option value={1536}>1536</option>
                </Select>
              </Field>

              <Field>
                <Label>Height</Label>
                <Select
                  value={height}
                  onChange={(e) => setHeight(parseInt(e.target.value))}
                >
                  <option value={512}>512</option>
                  <option value={768}>768</option>
                  <option value={1024}>1024</option>
                  <option value={1280}>1280</option>
                  <option value={1536}>1536</option>
                </Select>
              </Field>
            </div>

            <Field>
              <Label>Seed (-1 for random)</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(parseInt(e.target.value))}
                  className="flex-1"
                />
                <Button onClick={() => setSeed(-1)} outline>
                  Random
                </Button>
              </div>
            </Field>

            <details className="group">
              <summary className="flex cursor-pointer items-center gap-2 text-sm/6 font-medium text-zinc-950 dark:text-white">
                <svg className="size-4 group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                Advanced Settings
              </summary>
              <div className="mt-4 space-y-4">
                <Field>
                  <Label>Denoise: {denoise}</Label>
                  <input
                    type="range"
                    value={denoise}
                    onChange={(e) => setDenoise(parseFloat(e.target.value))}
                    min={0}
                    max={1}
                    step={0.05}
                    className="w-full"
                  />
                  <Text className="mt-1">
                    1.0 = full generation, lower values for img2img refinement
                  </Text>
                </Field>

                <Field>
                  <Label>Scheduler (optional)</Label>
                  <Input
                    type="text"
                    value={scheduler}
                    onChange={(e) => setScheduler(e.target.value)}
                    placeholder="e.g. karras, normal"
                  />
                </Field>
              </div>
            </details>

            <div className="pt-4">
              <Button
                onClick={handleGenerate}
                disabled={generateMutation.isPending || !prompt.trim() || !selectedModel}
                className="w-full"
              >
                {generateMutation.isPending ? 'Generating...' : 'Generate Image'}
              </Button>
              {generateMutation.error && (
                <Text className="mt-2 text-red-600 dark:text-red-400">
                  Error: {generateMutation.error instanceof Error ? generateMutation.error.message : 'Unknown error'}
                </Text>
              )}
            </div>
          </div>
        </div>

        {/* Preview */}
        <div>
          <Heading level={2}>Preview</Heading>
          <Divider className="my-4" soft />

          {generateMutation.isPending ? (
            <div className="flex flex-col items-center justify-center py-32">
              <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-zinc-950 dark:border-white"></div>
              <Text className="mt-4">Generating image...</Text>
              <Text className="mt-2">This may take a few seconds</Text>
            </div>
          ) : generatedImage ? (
            <div className="space-y-4">
              <div className="relative overflow-hidden rounded-lg bg-zinc-100 dark:bg-zinc-800">
                <Image
                  src={apiClient.getImageUrl(generatedImage.experiment_id, generatedImage.image_path.split('/').pop()!)}
                  alt="Generated image"
                  width={width}
                  height={height}
                  className="w-full h-auto"
                  unoptimized
                />
              </div>

              <div className="rounded-lg bg-zinc-100 p-4 dark:bg-zinc-800">
                <Text className="font-medium">Generation Details</Text>
                <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Model:</Text>
                    <Text className="font-medium">{generatedImage.metadata.model}</Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Steps:</Text>
                    <Text className="font-medium">{generatedImage.metadata.steps}</Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">CFG Scale:</Text>
                    <Text className="font-medium">{generatedImage.metadata.cfg_scale}</Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Seed:</Text>
                    <Text className="font-medium">{generatedImage.metadata.seed}</Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Dimensions:</Text>
                    <Text className="font-medium">
                      {generatedImage.metadata.width}×{generatedImage.metadata.height}
                    </Text>
                  </div>
                  {generatedImage.metadata.scheduler && (
                    <div>
                      <Text className="text-zinc-600 dark:text-zinc-400">Scheduler:</Text>
                      <Text className="font-medium">{generatedImage.metadata.scheduler}</Text>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  href={apiClient.getImageUrl(generatedImage.experiment_id, generatedImage.image_path.split('/').pop()!)}
                  download
                  className="flex-1"
                  outline
                >
                  Download
                </Button>
                <Button
                  onClick={() => setSeed(generatedImage.metadata.seed)}
                  className="flex-1"
                >
                  Use This Seed
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-zinc-500 dark:text-zinc-400">
              <svg
                className="mb-4 h-16 w-16"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <Text>Generated image will appear here</Text>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
