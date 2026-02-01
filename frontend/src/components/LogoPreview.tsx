import React from 'react';

interface LogoPreviewProps {
  logoUrl: string;
  onDownload: () => void;
  onReset: () => void;
}

export const LogoPreview: React.FC<LogoPreviewProps> = ({ logoUrl, onDownload, onReset }) => {
  return (
    <div className="flex flex-col items-center space-y-6">
      <div className="relative bg-white p-4 rounded-xl shadow-lg">
        <img
          src={logoUrl}
          alt="Generated Logo"
          className="max-w-full h-auto max-h-80 object-contain"
        />
      </div>

      <div className="flex gap-4">
        <button
          onClick={onDownload}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download Logo
        </button>

        <button
          onClick={onReset}
          className="px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-colors"
        >
          Generate New
        </button>
      </div>
    </div>
  );
};
