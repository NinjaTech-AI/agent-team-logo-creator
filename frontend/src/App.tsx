import { useState } from 'react';
import { LogoInputForm, LoadingState, LogoPreview } from './components';
import { generateLogo, improvePrompt } from './services/api';
import type { LogoStyle, LogoSize, LogoResolution, LogoFilter } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [isImproving, setIsImproving] = useState(false);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [improvedPrompt, setImprovedPrompt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPromptDialog, setShowPromptDialog] = useState(false);
  const [currentParams, setCurrentParams] = useState<any>(null);

  const handleGenerate = async (params: {
    businessName: string;
    style: LogoStyle;
    description?: string;
    size?: LogoSize;
    resolution?: LogoResolution;
    filters?: LogoFilter[];
    transparency?: boolean;
  }) => {
    setIsLoading(true);
    setError(null);
    setLogoUrl(null);
    setPreviewUrl(null);

    try {
      const response = await generateLogo({
        business_name: params.businessName,
        style: params.style,
        description: params.description,
        size: params.size,
        resolution: params.resolution,
        filters: params.filters,
        transparency: params.transparency,
        preview_mode: false,
      });

      if (response.success && response.logo_url) {
        setLogoUrl(response.logo_url);
      } else {
        setError(response.error || 'Failed to generate logo');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreview = async (params: {
    businessName: string;
    style: LogoStyle;
    description?: string;
    filters?: LogoFilter[];
    transparency?: boolean;
  }) => {
    setIsLoading(true);
    setError(null);
    setPreviewUrl(null);

    try {
      const response = await generateLogo({
        business_name: params.businessName,
        style: params.style,
        description: params.description,
        filters: params.filters,
        transparency: params.transparency,
        preview_mode: true,
      });

      if (response.success && response.logo_url) {
        setPreviewUrl(response.logo_url);
      } else {
        setError(response.error || 'Failed to generate preview');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImprovePrompt = async (params: {
    businessName: string;
    style: LogoStyle;
    description?: string;
  }) => {
    setIsImproving(true);
    setError(null);
    setCurrentParams(params);

    try {
      const response = await improvePrompt({
        business_name: params.businessName,
        style: params.style,
        description: params.description,
      });

      if (response.success && response.improved_prompt) {
        setImprovedPrompt(response.improved_prompt);
        if (response.preview_url) {
          setPreviewUrl(response.preview_url);
        }
        setShowPromptDialog(true);
      } else {
        setError(response.error || 'Failed to improve prompt');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsImproving(false);
    }
  };

  const handleAcceptImprovedPrompt = async () => {
    if (!currentParams) return;

    setShowPromptDialog(false);
    setIsLoading(true);
    setError(null);
    setLogoUrl(null);

    try {
      // Generate with improved prompt (description)
      const response = await generateLogo({
        business_name: currentParams.businessName,
        style: currentParams.style,
        description: improvedPrompt || currentParams.description,
        preview_mode: false,
      });

      if (response.success && response.logo_url) {
        setLogoUrl(response.logo_url);
      } else {
        setError(response.error || 'Failed to generate logo');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
      setImprovedPrompt(null);
      setCurrentParams(null);
    }
  };

  const handleDeclineImprovedPrompt = () => {
    setShowPromptDialog(false);
    setImprovedPrompt(null);
    setPreviewUrl(null);
    setCurrentParams(null);
  };

  const handleDownload = async () => {
    const urlToDownload = logoUrl || previewUrl;
    if (!urlToDownload) return;

    try {
      const response = await fetch(urlToDownload);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = logoUrl ? 'logo.png' : 'logo-preview.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleReset = () => {
    setLogoUrl(null);
    setPreviewUrl(null);
    setError(null);
    setImprovedPrompt(null);
    setShowPromptDialog(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Logo Creator
          </h1>
          <p className="text-lg text-gray-600">
            Generate unique logos for your business with the power of AI
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {/* AI Prompt Improver Dialog - #37 */}
          {showPromptDialog && improvedPrompt && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  ✨ AI-Improved Prompt
                </h2>
                
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Enhanced Description:</h3>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <p className="text-gray-800 whitespace-pre-wrap">{improvedPrompt}</p>
                  </div>
                </div>

                {previewUrl && (
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Preview:</h3>
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <img
                        src={previewUrl}
                        alt="Improved prompt preview"
                        className="w-full max-w-md mx-auto rounded-lg shadow-lg"
                      />
                    </div>
                  </div>
                )}

                <div className="flex gap-4">
                  <button
                    onClick={handleAcceptImprovedPrompt}
                    className="flex-1 py-3 px-6 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
                  >
                    ✓ Accept & Generate Full Resolution
                  </button>
                  <button
                    onClick={handleDeclineImprovedPrompt}
                    className="flex-1 py-3 px-6 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    ✗ Decline
                  </button>
                </div>
              </div>
            </div>
          )}

          {isLoading ? (
            <LoadingState />
          ) : (logoUrl || previewUrl) ? (
            <div className="space-y-6">
              <LogoPreview
                logoUrl={logoUrl || previewUrl!}
                onDownload={handleDownload}
                onReset={handleReset}
              />
              {previewUrl && !logoUrl && (
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-4">
                    This is a quick preview. Generate full resolution for the best quality.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <LogoInputForm
              onGenerate={handleGenerate}
              onPreview={handlePreview}
              onImprovePrompt={handleImprovePrompt}
              isLoading={isLoading}
              isImproving={isImproving}
            />
          )}
        </main>

        <footer className="text-center mt-16 text-gray-500 text-sm">
          <p>Powered by GPT Image Generator 1.5</p>
          <p className="mt-2">
            ✨ Features: AI Prompt Improver • Quick Preview • Custom Sizes • Visual Effects • Transparency
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;