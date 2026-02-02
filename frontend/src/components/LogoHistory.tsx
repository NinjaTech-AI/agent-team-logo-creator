import React from 'react';

export interface LogoHistoryItem {
  id: string;
  url: string;
  timestamp: number;
  businessName: string;
  style: string;
}

interface LogoHistoryProps {
  history: LogoHistoryItem[];
  onSelect: (item: LogoHistoryItem) => void;
  onClear: () => void;
}

export const LogoHistory: React.FC<LogoHistoryProps> = ({ history, onSelect, onClear }) => {
  if (history.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 text-center">
        <p className="text-gray-500">No logo history yet. Generate your first logo!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">Logo History</h2>
        <button
          onClick={onClear}
          className="text-sm text-red-600 hover:text-red-700 font-medium"
        >
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {history.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelect(item)}
            className="group cursor-pointer relative bg-gray-50 rounded-lg p-2 hover:bg-gray-100 transition-colors border-2 border-transparent hover:border-blue-500"
          >
            <div className="aspect-square bg-white rounded overflow-hidden mb-2">
              <img
                src={item.url}
                alt={`Logo for ${item.businessName}`}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="text-xs">
              <p className="font-medium text-gray-900 truncate">{item.businessName}</p>
              <p className="text-gray-500 truncate">{item.style}</p>
              <p className="text-gray-400">
                {new Date(item.timestamp).toLocaleDateString()}
              </p>
            </div>
            <div className="absolute inset-0 bg-blue-600 bg-opacity-0 group-hover:bg-opacity-10 rounded-lg transition-all flex items-center justify-center">
              <span className="text-white opacity-0 group-hover:opacity-100 font-semibold">
                View
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};