import React, { useState } from 'react';
import type { LogoStyle } from '../types';

interface LogoInputFormProps {
  onGenerate: (businessName: string, style: LogoStyle) => void;
  isLoading: boolean;
}

const LOGO_STYLES: { value: LogoStyle; label: string }[] = [
  { value: 'minimalist', label: 'Minimalist' },
  { value: 'modern', label: 'Modern' },
  { value: 'classic', label: 'Classic' },
  { value: 'playful', label: 'Playful' },
  { value: 'professional', label: 'Professional' },
  { value: 'vintage', label: 'Vintage' },
];

export const LogoInputForm: React.FC<LogoInputFormProps> = ({ onGenerate, isLoading }) => {
  const [businessName, setBusinessName] = useState('');
  const [style, setStyle] = useState<LogoStyle>('modern');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (businessName.trim()) {
      onGenerate(businessName.trim(), style);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto space-y-6">
      <div>
        <label htmlFor="businessName" className="block text-sm font-medium text-gray-700 mb-2">
          Business Name
        </label>
        <input
          type="text"
          id="businessName"
          value={businessName}
          onChange={(e) => setBusinessName(e.target.value)}
          placeholder="Enter your business name"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          disabled={isLoading}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Logo Style
        </label>
        <div className="grid grid-cols-3 gap-2">
          {LOGO_STYLES.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              onClick={() => setStyle(value)}
              disabled={isLoading}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                style === value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading || !businessName.trim()}
        className="w-full py-3 px-6 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Generating...' : 'Generate Logo'}
      </button>
    </form>
  );
};
