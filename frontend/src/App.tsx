import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { LogoForm } from './components/LogoForm';
import { LogoPreview } from './components/LogoPreview';
import { DownloadPanel } from './components/DownloadPanel';
import { generateLogo, getStyles } from './api';
import type { StylePreset, LogoResponse } from './types';

export default function App() {
  const [generatedLogo, setGeneratedLogo] = useState<LogoResponse | null>(null);

  const { data: styles = [] } = useQuery({
    queryKey: ['styles'],
    queryFn: getStyles,
    staleTime: Infinity,
  });

  const generateMutation = useMutation({
    mutationFn: ({
      description,
      style,
    }: {
      description: string;
      style: StylePreset | null;
    }) => generateLogo({ description, style: style ?? undefined }),
    onSuccess: (data) => {
      setGeneratedLogo(data);
    },
  });

  const handleGenerate = (description: string, style: StylePreset | null) => {
    generateMutation.mutate({ description, style });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Logo Creator</span>
            </div>
            <span className="text-sm text-gray-500">AI-Powered Design</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {/* Hero section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Create Your Perfect Logo
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Describe your vision and let AI generate a professional logo in seconds.
            No design skills required.
          </p>
        </div>

        {/* Two-column layout */}
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Left column - Form */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 lg:p-8">
              <LogoForm
                styles={styles}
                onSubmit={handleGenerate}
                isLoading={generateMutation.isPending}
                error={
                  generateMutation.isError
                    ? generateMutation.error instanceof Error
                      ? generateMutation.error.message
                      : 'Failed to generate logo'
                    : null
                }
              />
            </div>
          </div>

          {/* Right column - Preview and Download */}
          <div className="space-y-6">
            {/* Preview */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 lg:p-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Preview</h2>
              <LogoPreview
                imageBase64={generatedLogo?.image_base64 ?? null}
                isLoading={generateMutation.isPending}
              />
            </div>

            {/* Download */}
            <DownloadPanel
              imageBase64={generatedLogo?.image_base64 ?? null}
              disabled={generateMutation.isPending}
            />

            {/* Generation info */}
            {generatedLogo && !generateMutation.isPending && (
              <div className="bg-white rounded-xl border border-gray-200 p-4 text-sm text-gray-500">
                <p>
                  <span className="font-medium">Style:</span>{' '}
                  {generatedLogo.style_applied ?? 'None'}
                </p>
                <p>
                  <span className="font-medium">Generation time:</span>{' '}
                  {(generatedLogo.generation_time_ms / 1000).toFixed(1)}s
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-16 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
          <p>Logo Creator - AI-Powered Logo Generation</p>
        </div>
      </footer>
    </div>
  );
}
