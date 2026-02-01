import React from 'react';

export const LoadingState: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-spin border-t-blue-600"></div>
      </div>
      <p className="mt-4 text-gray-600 text-lg">Creating your logo...</p>
      <p className="mt-2 text-gray-400 text-sm">This may take a few seconds</p>
    </div>
  );
};
