import { useState } from 'react';
import { LogoInputForm, LoadingState, LogoPreview } from './components';
import { generateLogo } from './services/api';
import type { LogoStyle } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (businessName: string, style: LogoStyle) => {
    setIsLoading(true);
    setError(null);
    setLogoUrl(null);

    try {
      const response = await generateLogo({ business_name: businessName, style });
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

  const handleDownload = async () => {
    if (!logoUrl) return;

    try {
      const response = await fetch(logoUrl);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'logo.png';
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
    setError(null);
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

        <main className="max-w-2xl mx-auto">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {isLoading ? (
            <LoadingState />
          ) : logoUrl ? (
            <LogoPreview
              logoUrl={logoUrl}
              onDownload={handleDownload}
              onReset={handleReset}
            />
          ) : (
            <LogoInputForm onGenerate={handleGenerate} isLoading={isLoading} />
          )}
        </main>

        <footer className="text-center mt-16 text-gray-500 text-sm">
          Powered by GPT Image Generator 1.5
        </footer>
      </div>
    </div>
  );
}

export default App;
