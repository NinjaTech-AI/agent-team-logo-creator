import React, { useState, useEffect } from 'react';

interface ProgressLoaderProps {
  stage: 'analyzing' | 'generating' | 'finalizing';
}

const stages = {
  analyzing: {
    message: 'Analyzing your request...',
    progress: 33,
    icon: '🔍',
  },
  generating: {
    message: 'Generating your logo...',
    progress: 66,
    icon: '🎨',
  },
  finalizing: {
    message: 'Almost done! Finalizing...',
    progress: 90,
    icon: '✨',
  },
};

export const ProgressLoader: React.FC<ProgressLoaderProps> = ({ stage }) => {
  const [dots, setDots] = useState('');
  const currentStage = stages[stage];

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center space-y-6 p-8">
      {/* Icon */}
      <div className="text-6xl animate-bounce">
        {currentStage.icon}
      </div>

      {/* Message */}
      <div className="text-center">
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          {currentStage.message}{dots}
        </h3>
        <p className="text-sm text-gray-600">
          This may take a few moments
        </p>
      </div>

      {/* Progress Bar */}
      <div className="w-full max-w-md">
        <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-full transition-all duration-500 ease-out"
            style={{ width: `${currentStage.progress}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>Starting</span>
          <span>{currentStage.progress}%</span>
          <span>Complete</span>
        </div>
      </div>

      {/* Console Output */}
      <div className="w-full max-w-md bg-gray-900 rounded-lg p-4 font-mono text-xs text-green-400">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-gray-500">$</span>
            <span>Initializing AI model...</span>
            <span className="text-green-500">✓</span>
          </div>
          {stage !== 'analyzing' && (
            <div className="flex items-center gap-2">
              <span className="text-gray-500">$</span>
              <span>Processing request parameters...</span>
              <span className="text-green-500">✓</span>
            </div>
          )}
          {stage === 'finalizing' && (
            <div className="flex items-center gap-2">
              <span className="text-gray-500">$</span>
              <span>Rendering final image...</span>
              <span className="text-yellow-500 animate-pulse">⟳</span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <span className="text-gray-500">$</span>
            <span className="animate-pulse">_</span>
          </div>
        </div>
      </div>

      {/* Spinner */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
        <span className="text-sm text-gray-600">Please wait...</span>
      </div>
    </div>
  );
};