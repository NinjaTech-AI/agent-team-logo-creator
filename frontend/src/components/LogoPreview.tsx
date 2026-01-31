import { useState } from 'react';
import { ZoomIn, ZoomOut, Sun, Moon, Grid3X3 } from 'lucide-react';
import { clsx } from 'clsx';
import type { BackgroundMode } from '../types';

interface LogoPreviewProps {
  imageBase64: string | null;
  isLoading: boolean;
}

export function LogoPreview({ imageBase64, isLoading }: LogoPreviewProps) {
  const [zoom, setZoom] = useState(1);
  const [background, setBackground] = useState<BackgroundMode>('light');

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 2));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));

  const backgroundStyles: Record<BackgroundMode, string> = {
    light: 'bg-white',
    dark: 'bg-gray-900',
    transparent: 'bg-[url("data:image/svg+xml,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20width%3D%2210%22%20height%3D%2210%22%20fill%3D%22%23e5e7eb%22%2F%3E%3Crect%20x%3D%2210%22%20y%3D%2210%22%20width%3D%2210%22%20height%3D%2210%22%20fill%3D%22%23e5e7eb%22%2F%3E%3C%2Fsvg%3E")]',
  };

  return (
    <div className="space-y-4">
      {/* Background toggle */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Preview Background</span>
        <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setBackground('light')}
            className={clsx(
              'p-2 rounded-md transition-colors',
              background === 'light'
                ? 'bg-white shadow text-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            )}
            title="Light background"
          >
            <Sun size={16} />
          </button>
          <button
            onClick={() => setBackground('dark')}
            className={clsx(
              'p-2 rounded-md transition-colors',
              background === 'dark'
                ? 'bg-gray-800 shadow text-white'
                : 'text-gray-500 hover:text-gray-700'
            )}
            title="Dark background"
          >
            <Moon size={16} />
          </button>
          <button
            onClick={() => setBackground('transparent')}
            className={clsx(
              'p-2 rounded-md transition-colors',
              background === 'transparent'
                ? 'bg-white shadow text-gray-900'
                : 'text-gray-500 hover:text-gray-700'
            )}
            title="Transparent (checkerboard)"
          >
            <Grid3X3 size={16} />
          </button>
        </div>
      </div>

      {/* Preview area */}
      <div
        className={clsx(
          'relative rounded-xl border-2 border-gray-200 overflow-hidden',
          'aspect-square max-w-md mx-auto',
          backgroundStyles[background]
        )}
      >
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-gray-600 font-medium">Generating your logo...</p>
              <p className="text-sm text-gray-400">This may take up to 30 seconds</p>
            </div>
          </div>
        ) : imageBase64 ? (
          <div
            className="absolute inset-0 flex items-center justify-center p-4"
            style={{ transform: `scale(${zoom})`, transition: 'transform 0.2s ease-out' }}
          >
            <img
              src={`data:image/png;base64,${imageBase64}`}
              alt="Generated logo"
              className="max-w-full max-h-full object-contain"
            />
          </div>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            <div className="text-center space-y-2">
              <div className="w-24 h-24 mx-auto border-4 border-dashed border-gray-300 rounded-xl flex items-center justify-center">
                <span className="text-4xl">?</span>
              </div>
              <p className="text-sm">Your logo will appear here</p>
            </div>
          </div>
        )}
      </div>

      {/* Zoom controls */}
      {imageBase64 && !isLoading && (
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 0.5}
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Zoom out"
          >
            <ZoomOut size={20} />
          </button>
          <span className="text-sm text-gray-600 w-16 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            disabled={zoom >= 2}
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Zoom in"
          >
            <ZoomIn size={20} />
          </button>
        </div>
      )}
    </div>
  );
}
