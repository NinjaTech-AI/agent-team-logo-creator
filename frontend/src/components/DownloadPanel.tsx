import { useState } from 'react';
import { Download, Check } from 'lucide-react';
import { clsx } from 'clsx';
import { downloadLogo } from '../api';

interface DownloadPanelProps {
  imageBase64: string | null;
  disabled?: boolean;
}

const SIZES = [
  { value: 256 as const, label: 'Small', description: '256 x 256 px' },
  { value: 512 as const, label: 'Medium', description: '512 x 512 px' },
  { value: 1024 as const, label: 'Large', description: '1024 x 1024 px' },
];

export function DownloadPanel({ imageBase64, disabled = false }: DownloadPanelProps) {
  const [selectedSize, setSelectedSize] = useState<256 | 512 | 1024>(512);
  const [transparent, setTransparent] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (!imageBase64) return;

    setIsDownloading(true);
    try {
      const blob = await downloadLogo(imageBase64, selectedSize, transparent);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logo_${selectedSize}px.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download logo. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const isDisabled = disabled || !imageBase64 || isDownloading;

  return (
    <div className="space-y-6 p-6 bg-gray-50 rounded-xl">
      <h3 className="text-lg font-semibold text-gray-900">Download Options</h3>

      {/* Size selection */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">Size</label>
        <div className="grid grid-cols-3 gap-3">
          {SIZES.map((size) => (
            <button
              key={size.value}
              type="button"
              disabled={isDisabled}
              onClick={() => setSelectedSize(size.value)}
              className={clsx(
                'p-3 rounded-lg border-2 text-center transition-all',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
                selectedSize === size.value
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 bg-white hover:border-gray-300',
                isDisabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              <div className="font-medium text-gray-900">{size.label}</div>
              <div className="text-xs text-gray-500">{size.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Transparency toggle */}
      <div className="flex items-center justify-between">
        <div>
          <label className="text-sm font-medium text-gray-700">
            Transparent Background
          </label>
          <p className="text-xs text-gray-500">Remove background for versatile use</p>
        </div>
        <button
          type="button"
          disabled={isDisabled}
          onClick={() => setTransparent(!transparent)}
          className={clsx(
            'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
            transparent ? 'bg-indigo-600' : 'bg-gray-300',
            isDisabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <span
            className={clsx(
              'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
              transparent ? 'translate-x-6' : 'translate-x-1'
            )}
          />
        </button>
      </div>

      {/* Download button */}
      <button
        onClick={handleDownload}
        disabled={isDisabled}
        className={clsx(
          'w-full py-3 px-4 rounded-lg font-medium transition-all',
          'flex items-center justify-center gap-2',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
          isDisabled
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-indigo-600 text-white hover:bg-indigo-700'
        )}
      >
        {isDownloading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Downloading...
          </>
        ) : (
          <>
            <Download size={20} />
            Download PNG
          </>
        )}
      </button>

      {!imageBase64 && (
        <p className="text-sm text-center text-gray-500">
          Generate a logo first to enable downloads
        </p>
      )}
    </div>
  );
}
