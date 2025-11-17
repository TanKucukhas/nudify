'use client';

import { useState, useMemo } from 'react';
import { useQuery, useQueries, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import type { ExperimentSummary, ExperimentDetail, ImageInfo } from '@/lib/types';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';
import { Heading } from '@/components/heading';
import { Button } from '@/components/button';
import { Divider } from '@/components/divider';
import { Input } from '@/components/input';
import { Select } from '@/components/select';
import { Field, Label } from '@/components/fieldset';
import { Text } from '@/components/text';
import { Badge } from '@/components/badge';

interface ImageWithExperiment extends ImageInfo {
  experiment_id: string;
}

export default function GalleryPage() {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();
  const initialExperiment = searchParams.get('experiment') || '';

  const [selectedExperiment, setSelectedExperiment] = useState(initialExperiment);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedStage, setSelectedStage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<ImageWithExperiment | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareImages, setCompareImages] = useState<ImageWithExperiment[]>([]);

  // Fetch experiments list
  const { data: experimentsData } = useQuery({
    queryKey: ['experiments'],
    queryFn: () => apiClient.listExperiments(),
  });

  // Fetch models for filter
  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: () => apiClient.listModels(),
  });

  // Fetch all experiment details
  const experimentIds = experimentsData?.experiments.map(e => e.experiment_id) || [];
  const experimentQueries = useQueries({
    queries: experimentIds.map(id => ({
      queryKey: ['experiment', id],
      queryFn: () => apiClient.getExperiment(id),
      enabled: experimentIds.length > 0,
    })),
  });

  // Combine all images from all experiments
  const allImages: ImageWithExperiment[] = useMemo(() => {
    const images: ImageWithExperiment[] = [];

    experimentQueries.forEach(query => {
      if (query.data) {
        query.data.images.forEach(img => {
          images.push({
            ...img,
            experiment_id: query.data.experiment_id,
          });
        });
      }
    });

    // Sort by creation time (newest first)
    return images.sort((a, b) => b.created_at - a.created_at);
  }, [experimentQueries]);

  // Get unique stages from all experiments
  const uniqueStages = useMemo(() => {
    const stages = new Set<string>();
    experimentsData?.experiments.forEach(exp => {
      exp.stages.forEach(stage => stages.add(stage));
    });
    return Array.from(stages).sort();
  }, [experimentsData]);

  // Filter images
  const filteredImages = useMemo(() => {
    return allImages.filter(img => {
      // Filter by experiment
      if (selectedExperiment && img.experiment_id !== selectedExperiment) {
        return false;
      }

      // Filter by stage (from filename)
      if (selectedStage) {
        const fileStage = img.filename.split('_')[0];
        if (fileStage !== selectedStage) {
          return false;
        }
      }

      // Search in filename (basic search)
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!img.filename.toLowerCase().includes(query) &&
            !img.experiment_id.toLowerCase().includes(query)) {
          return false;
        }
      }

      return true;
    });
  }, [allImages, selectedExperiment, selectedStage, searchQuery]);

  // Delete experiment mutation
  const deleteMutation = useMutation({
    mutationFn: (experimentId: string) => apiClient.deleteExperiment(experimentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
      setSelectedImage(null);
    },
  });

  const handleImageClick = (img: ImageWithExperiment) => {
    if (compareMode) {
      if (compareImages.find(i => i.filename === img.filename && i.experiment_id === img.experiment_id)) {
        setCompareImages(compareImages.filter(i => !(i.filename === img.filename && i.experiment_id === img.experiment_id)));
      } else if (compareImages.length < 4) {
        setCompareImages([...compareImages, img]);
      }
    } else {
      setSelectedImage(img);
    }
  };

  const clearFilters = () => {
    setSelectedExperiment('');
    setSelectedModel('');
    setSelectedStage('');
    setSearchQuery('');
  };

  return (
    <div>
      <Heading>Image Gallery</Heading>
      <Text>Browse and manage generated images</Text>
      <Divider className="my-10 mt-6" />

      {/* Filters */}
      <div className="mb-8">
        <div className="flex items-end justify-between gap-4 mb-4">
          <Heading level={2}>Filters</Heading>
          <div className="flex gap-2">
            <Button
              onClick={() => setCompareMode(!compareMode)}
              color={compareMode ? 'purple' : 'zinc'}
              outline={!compareMode}
            >
              {compareMode ? `Compare (${compareImages.length}/4)` : 'Compare Mode'}
            </Button>
            <Button onClick={clearFilters} outline>
              Clear Filters
            </Button>
          </div>
        </div>
        <Divider className="mb-4" soft />

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          {/* Search */}
          <Field>
            <Label>Search</Label>
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search filenames..."
            />
          </Field>

          {/* Experiment Filter */}
          <Field>
            <Label>Experiment</Label>
            <Select
              value={selectedExperiment}
              onChange={(e) => setSelectedExperiment(e.target.value)}
            >
              <option value="">All Experiments</option>
              {experimentsData?.experiments.map(exp => (
                <option key={exp.experiment_id} value={exp.experiment_id}>
                  {exp.experiment_id} ({exp.image_count})
                </option>
              ))}
            </Select>
          </Field>

          {/* Stage Filter */}
          <Field>
            <Label>Stage</Label>
            <Select
              value={selectedStage}
              onChange={(e) => setSelectedStage(e.target.value)}
            >
              <option value="">All Stages</option>
              {uniqueStages.map(stage => (
                <option key={stage} value={stage}>
                  {stage}
                </option>
              ))}
            </Select>
          </Field>

          {/* Results Count */}
          <Field>
            <Label>Results</Label>
            <div className="rounded-md border border-zinc-950/10 bg-zinc-50 px-3 py-2 dark:border-white/10 dark:bg-zinc-900">
              <Text className="font-medium">{filteredImages.length} images</Text>
            </div>
          </Field>
        </div>
      </div>

      {/* Compare View */}
      {compareMode && compareImages.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <Heading level={2}>Comparing {compareImages.length} images</Heading>
            <Button onClick={() => setCompareImages([])} color="red" outline>
              Clear Selection
            </Button>
          </div>
          <Divider className="mb-4" soft />
          <div className={`grid grid-cols-${Math.min(compareImages.length, 4)} gap-4`}>
            {compareImages.map((img) => (
              <div key={`${img.experiment_id}-${img.filename}`} className="space-y-2">
                <div className="relative overflow-hidden rounded-lg bg-zinc-100 dark:bg-zinc-800 aspect-square">
                  <Image
                    src={apiClient.getImageUrl(img.experiment_id, img.filename)}
                    alt={img.filename}
                    fill
                    className="object-contain"
                    unoptimized
                  />
                </div>
                <Text className="truncate text-xs">{img.filename}</Text>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Image Grid */}
      {filteredImages.length === 0 ? (
        <div className="rounded-lg bg-zinc-50 dark:bg-zinc-900 p-12 text-center">
          <svg
            className="mx-auto mb-4 h-16 w-16 text-zinc-400 dark:text-zinc-600"
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
          <Text className="text-zinc-500 dark:text-zinc-400">No images found</Text>
          <Text className="mt-2">Try adjusting your filters or generate some images</Text>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {filteredImages.map((img) => {
            const isSelected = compareMode && compareImages.find(
              i => i.filename === img.filename && i.experiment_id === img.experiment_id
            );

            return (
              <div
                key={`${img.experiment_id}-${img.filename}`}
                onClick={() => handleImageClick(img)}
                className={`relative overflow-hidden rounded-lg bg-white dark:bg-zinc-900 shadow cursor-pointer transition-shadow hover:shadow-lg ${
                  isSelected ? 'ring-4 ring-purple-500' : ''
                }`}
              >
                <div className="relative aspect-square bg-zinc-100 dark:bg-zinc-800">
                  <Image
                    src={apiClient.getImageUrl(img.experiment_id, img.filename)}
                    alt={img.filename}
                    fill
                    className="object-contain"
                    unoptimized
                  />
                </div>
                <div className="p-3">
                  <Text className="truncate font-medium">
                    {img.filename}
                  </Text>
                  <Text className="truncate text-zinc-500 dark:text-zinc-400">
                    {img.experiment_id}
                  </Text>
                  <Text className="mt-1 text-zinc-400 dark:text-zinc-500">
                    {new Date(img.created_at * 1000).toLocaleDateString()}
                  </Text>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div
            className="w-full max-w-6xl max-h-[90vh] overflow-auto rounded-lg bg-white dark:bg-zinc-900"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="mb-4 flex items-center justify-between">
                <Heading level={2}>
                  {selectedImage.filename}
                </Heading>
                <button
                  onClick={() => setSelectedImage(null)}
                  className="text-zinc-400 hover:text-zinc-600 dark:text-zinc-500 dark:hover:text-zinc-300"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Image */}
              <div className="mb-4 relative rounded-lg bg-zinc-100 dark:bg-zinc-800" style={{ maxHeight: '60vh' }}>
                <Image
                  src={apiClient.getImageUrl(selectedImage.experiment_id, selectedImage.filename)}
                  alt={selectedImage.filename}
                  width={1024}
                  height={1024}
                  className="h-auto w-full rounded-lg"
                  unoptimized
                />
              </div>

              {/* Metadata */}
              <div className="mb-4 rounded-lg bg-zinc-50 dark:bg-zinc-800 p-4">
                <Text className="mb-2 font-medium">Details</Text>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Experiment:</Text>
                    <Text className="font-medium">{selectedImage.experiment_id}</Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">File Size:</Text>
                    <Text className="font-medium">
                      {(selectedImage.size_bytes / 1024 / 1024).toFixed(2)} MB
                    </Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Created:</Text>
                    <Text className="font-medium">
                      {new Date(selectedImage.created_at * 1000).toLocaleString()}
                    </Text>
                  </div>
                  <div>
                    <Text className="text-zinc-600 dark:text-zinc-400">Path:</Text>
                    <Text className="truncate font-medium text-xs">{selectedImage.path}</Text>
                  </div>
                </dl>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  href={apiClient.getImageUrl(selectedImage.experiment_id, selectedImage.filename)}
                  download
                  className="flex-1"
                >
                  Download
                </Button>
                <Button
                  onClick={() => {
                    if (confirm(`Delete entire experiment "${selectedImage.experiment_id}"? This will remove all images.`)) {
                      deleteMutation.mutate(selectedImage.experiment_id);
                    }
                  }}
                  disabled={deleteMutation.isPending}
                  color="red"
                  className="flex-1"
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete Experiment'}
                </Button>
              </div>
              {deleteMutation.error && (
                <Text className="mt-2 text-red-600 dark:text-red-400">
                  Error: {deleteMutation.error instanceof Error ? deleteMutation.error.message : 'Unknown error'}
                </Text>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
