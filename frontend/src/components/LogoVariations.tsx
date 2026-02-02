import React, { useState } from 'react';

interface LogoVariationsProps {
  logoUrls: string[];
  onDownload: (url: string) => void;
  onReset: () => void;
}

export const LogoVariations: React.FC<LogoVariationsProps> = ({ logoUrls, onDownload, onReset }) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <div className="flex flex-col items-center space-y-6">
      {/* Main Selected Logo */}
      <div className="relative bg-white p-4 rounded-xl shadow-lg">
        <img
          src={logoUrls[selectedIndex]}
          alt={`Generated Logo ${selectedIndex + 1}`}
          className="max-w-full h-auto max-h-80 object-contain"
        />
        <div className="absolute top-2 right-2 bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
          {selectedIndex + 1} of {logoUrls.length}
        </div>
      </div>

      {/* Variation Grid */}
      {logoUrls.length > 1 && (
        <div className="w-full">
          <h3 className="text-lg font-semibold text-gray-900 mb-3 text-center">
            Choose Your Favorite
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {logoUrls.map((url, index) => (
              <button
                key={index}
                onClick={() => setSelectedIndex(index)}
                className={`relative bg-white p-3 rounded-lg transition-all ${
                  selectedIndex === index
                    ? 'ring-4 ring-blue-500 shadow-lg scale-105'
                    : 'ring-2 ring-gray-200 hover:ring-blue-300 hover:shadow-md'
                }`}
              >
                <div className="aspect-square bg-gray-50 rounded overflow-hidden mb-2">
                  <img
                    src={url}
                    alt={`Variation ${index + 1}`}
                    className="w-full h-full object-contain"
                  />
                </div>
                <div className="flex items-center justify-center gap-2">
                  <div
                    className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                      selectedIndex === index
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300'
                    }`}
                  >
                    {selectedIndex === index && (
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    Option {index + 1}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={() => onDownload(logoUrls[selectedIndex])}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download Selected
        </button>

        <button
          onClick={onReset}
          className="px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-colors"
        >
          Generate New
        </button>
      </div>

      {logoUrls.length > 1 && (
        <p className="text-sm text-gray-600 text-center">
          💡 Tip: Click on any variation to select it, then download your favorite!
        </p>
      )}
    </div>
  );
};