import { useState, FormEvent } from 'react';
import { Sparkles, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { StyleSelector } from './StyleSelector';
import type { Style, StylePreset } from '../types';

interface LogoFormProps {
  styles: Style[];
  onSubmit: (description: string, style: StylePreset | null) => void;
  isLoading: boolean;
  error: string | null;
}

const EXAMPLE_PROMPTS = [
  'A modern tech startup logo for an AI company called Nexus',
  'A playful coffee shop logo with a smiling cup',
  'A professional law firm logo with scales of justice',
  'A vintage bakery logo with wheat and rolling pin',
  'A minimal fitness brand logo with abstract movement',
];

export function LogoForm({ styles, onSubmit, isLoading, error }: LogoFormProps) {
  const [description, setDescription] = useState('');
  const [selectedStyle, setSelectedStyle] = useState<StylePreset | null>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (description.trim().length >= 10) {
      onSubmit(description.trim(), selectedStyle);
    }
  };

  const handleExampleClick = (example: string) => {
    setDescription(example);
  };

  const charCount = description.length;
  const isValidLength = charCount >= 10 && charCount <= 500;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Description input */}
      <div className="space-y-2">
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700"
        >
          Describe your logo
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isLoading}
          placeholder="Describe the logo you want to create..."
          rows={4}
          className={clsx(
            'w-full px-4 py-3 rounded-lg border-2 resize-none',
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
            'placeholder:text-gray-400 transition-colors',
            error ? 'border-red-300' : 'border-gray-200 hover:border-gray-300',
            isLoading && 'bg-gray-50 cursor-not-allowed'
          )}
          maxLength={500}
        />
        <div className="flex justify-between text-sm">
          <span
            className={clsx(
              charCount > 0 && !isValidLength ? 'text-red-500' : 'text-gray-400'
            )}
          >
            {charCount < 10 && charCount > 0
              ? `${10 - charCount} more characters needed`
              : `${charCount}/500 characters`}
          </span>
        </div>
      </div>

      {/* Example prompts */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-500">
          Try an example:
        </label>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_PROMPTS.slice(0, 3).map((example, i) => (
            <button
              key={i}
              type="button"
              disabled={isLoading}
              onClick={() => handleExampleClick(example)}
              className={clsx(
                'text-xs px-3 py-1.5 rounded-full',
                'border border-gray-200 bg-white text-gray-600',
                'hover:border-indigo-300 hover:text-indigo-600 transition-colors',
                isLoading && 'opacity-50 cursor-not-allowed'
              )}
            >
              {example.slice(0, 40)}...
            </button>
          ))}
        </div>
      </div>

      {/* Style selector */}
      <StyleSelector
        styles={styles}
        selectedStyle={selectedStyle}
        onSelectStyle={setSelectedStyle}
        disabled={isLoading}
      />

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-2 p-4 rounded-lg bg-red-50 text-red-700">
          <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={!isValidLength || isLoading}
        className={clsx(
          'w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all',
          'flex items-center justify-center gap-3',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
          isValidLength && !isLoading
            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        )}
      >
        {isLoading ? (
          <>
            <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <Sparkles size={24} />
            Generate Logo
          </>
        )}
      </button>
    </form>
  );
}
