'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { Heading } from '@/components/heading';
import { Button } from '@/components/button';
import { Divider } from '@/components/divider';
import { Badge } from '@/components/badge';
import {
  SparklesIcon,
  Square3Stack3DIcon,
  PhotoIcon,
  CpuChipIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/16/solid';

export default function Dashboard() {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.health(),
    refetchInterval: 5000,
  });

  const { data: experimentsData } = useQuery({
    queryKey: ['experiments'],
    queryFn: () => apiClient.listExperiments(),
  });

  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: () => apiClient.listModels(),
  });

  const enabledModels = modelsData?.models.filter((m) => m.enabled) || [];
  const experiments = experimentsData?.experiments || [];

  return (
    <div>
      <div className="flex items-end justify-between gap-4">
        <Heading>Dashboard</Heading>
        <div className="flex gap-4">
          <Button href="/generate" outline>
            <SparklesIcon />
            Generate
          </Button>
          <Button href="/batch" color="green">
            <Square3Stack3DIcon />
            New Batch
          </Button>
        </div>
      </div>
      <Divider className="my-10 mt-6" />

      {/* Status Cards */}
      <div className="grid gap-8 sm:grid-cols-2 xl:grid-cols-3">
        {/* Backend Health */}
        <div>
          <Divider soft />
          <div className="mt-6">
            <div className="flex items-center gap-3">
              {health?.status === 'healthy' ? (
                <CheckCircleIcon className="size-8 text-green-500" />
              ) : (
                <XCircleIcon className="size-8 text-red-500" />
              )}
              <div>
                <div className="text-sm/6 font-medium text-zinc-500 dark:text-zinc-400">
                  Backend Status
                </div>
                <div className="text-2xl/8 font-semibold text-zinc-950 dark:text-white">
                  {healthLoading ? 'Loading...' : health?.status || 'Unknown'}
                </div>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-sm/6 text-zinc-600 dark:text-zinc-400">
                ComfyUI: <Badge color={health?.comfyui === 'connected' ? 'green' : 'red'}>
                  {health?.comfyui || 'unknown'}
                </Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Experiments */}
        <div>
          <Divider soft />
          <div className="mt-6">
            <div className="flex items-center gap-3">
              <PhotoIcon className="size-8 text-blue-500" />
              <div>
                <div className="text-sm/6 font-medium text-zinc-500 dark:text-zinc-400">
                  Total Experiments
                </div>
                <div className="text-2xl/8 font-semibold text-zinc-950 dark:text-white">
                  {experiments.length}
                </div>
              </div>
            </div>
            <div className="mt-4">
              <Button href="/gallery" outline>
                View Gallery
              </Button>
            </div>
          </div>
        </div>

        {/* Models */}
        <div>
          <Divider soft />
          <div className="mt-6">
            <div className="flex items-center gap-3">
              <CpuChipIcon className="size-8 text-purple-500" />
              <div>
                <div className="text-sm/6 font-medium text-zinc-500 dark:text-zinc-400">
                  Available Models
                </div>
                <div className="text-2xl/8 font-semibold text-zinc-950 dark:text-white">
                  {enabledModels.length}
                </div>
              </div>
            </div>
            <div className="mt-4">
              <Button href="/models" outline>
                Manage Models
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Experiments */}
      <Divider className="my-10" soft />
      <Heading level={2}>Recent Experiments</Heading>
      <div className="mt-6">
        {experiments.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-sm/6 text-zinc-600 dark:text-zinc-400">
              No experiments yet. Start by{' '}
              <Link href="/generate" className="text-blue-600 hover:text-blue-500 dark:text-blue-400">
                generating an image
              </Link>
              .
            </p>
          </div>
        ) : (
          <div className="mt-4 space-y-4">
            {experiments.slice(0, 5).map((exp) => (
              <div
                key={exp.experiment_id}
                className="flex items-center justify-between rounded-lg border border-zinc-950/10 px-4 py-3 dark:border-white/10"
              >
                <div>
                  <div className="text-base/6 font-semibold text-zinc-950 dark:text-white">
                    {exp.experiment_id}
                  </div>
                  <div className="text-sm/6 text-zinc-600 dark:text-zinc-400">
                    {exp.image_count} image{exp.image_count !== 1 ? 's' : ''} •{' '}
                    {exp.stages.join(', ') || 'no stages'}
                  </div>
                </div>
                <Button href={`/gallery?experiment=${exp.experiment_id}`} outline>
                  View
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
