import React, { useState } from 'react';
import type { LogoStyle, LogoSize, LogoResolution, LogoFilter } from '../types';

interface LogoInputFormProps {
  onGenerate: (params: {
    businessName: string;
    style: LogoStyle;
    description?: string;
    size?: LogoSize;
    resolution?: LogoResolution;
    filters?: LogoFilter[];
    transparency?: boolean;
  }) => void;
  onPreview: (params: {
    businessName: string;
    style: LogoStyle;
    description?: string;
    filters?: LogoFilter[];
    transparency?: boolean;
  }) => void;
  onImprovePrompt: (params: {
    businessName: string;
    style: LogoStyle;
    description?: string;
  }) => void;
  isLoading: boolean;
  isImproving: boolean;
}

const LOGO_STYLES: { value: LogoStyle; label: string }[] = [
  { value: 'minimalist', label: 'Minimalist' },
  { value: 'modern', label: 'Modern' },
  { value: 'classic', label: 'Classic' },
  { value: 'playful', label: 'Playful' },
  { value: 'professional', label: 'Professional' },
  { value: 'vintage', label: 'Vintage' },
];

const LOGO_SIZES: { value: LogoSize; label: string }[] = [
  { value: '1024x1024', label: 'Square (1024x1024)' },
  { value: '1792x1024', label: 'Landscape (1792x1024)' },
  { value: '1024x1792', label: 'Portrait (1024x1792)' },
];

const LOGO_RESOLUTIONS: { value: LogoResolution; label: string }[] = [
  { value: 'standard', label: 'Standard' },
  { value: 'high', label: 'High' },
  { value: 'hd', label: 'HD' },
];

const LOGO_FILTERS: { value: LogoFilter; label: string }[] = [
  { value: 'vibrant', label: 'Vibrant' },
  { value: 'muted', label: 'Muted' },
  { value: 'monochrome', label: 'Monochrome' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'neon', label: 'Neon' },
  { value: 'pastel', label: 'Pastel' },
  { value: 'bold', label: 'Bold' },
  { value: 'soft', label: 'Soft' },
];

export const LogoInputForm: React.FC<LogoInputFormProps> = ({ 
  onGenerate, 
  onPreview,
  onImprovePrompt,
  isLoading,
  isImproving 
}) => {
  const [businessName, setBusinessName] = useState('');
  const [style, setStyle] = useState<LogoStyle>('modern');
  const [description, setDescription] = useState('');
  const [size, setSize] = useState<LogoSize>('1024x1024');
  const [resolution, setResolution] = useState<LogoResolution>('high');
  const [selectedFilters, setSelectedFilters] = useState<LogoFilter[]>([]);
  const [transparency, setTransparency] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (businessName.trim()) {
      onGenerate({
        businessName: businessName.trim(),
        style,
        description: description.trim() || undefined,
        size,
        resolution,
        filters: selectedFilters.length > 0 ? selectedFilters : undefined,
        transparency,
      });
    }
  };

  const handlePreview = () => {
    if (businessName.trim()) {
      onPreview({
        businessName: businessName.trim(),
        style,
        description: description.trim() || undefined,
        filters: selectedFilters.length > 0 ? selectedFilters : undefined,
        transparency,
      });
    }
  };

  const handleImprovePrompt = () => {
    if (businessName.trim()) {
      onImprovePrompt({
        businessName: businessName.trim(),
        style,
        description: description.trim() || undefined,
      });
    }
  };

  const toggleFilter = (filter: LogoFilter) => {
    setSelectedFilters(prev =>
      prev.includes(filter)
        ? prev.filter(f => f !== filter)
        : [...prev, filter]
    );
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto space-y-6 bg-white p-8 rounded-xl shadow-lg">
      {/* Business Name */}
      <div>
        <label htmlFor="businessName" className="block text-sm font-medium text-gray-700 mb-2">
          Business Name *
        </label>
        <input
          type="text"
          id="businessName"
          value={businessName}
          onChange={(e) => setBusinessName(e.target.value)}
          placeholder="Enter your business name"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          disabled={isLoading || isImproving}
          required
        />
      </div>

      {/* Description/Story - #32 */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Brand Story (Optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Tell us about your brand, values, and what makes you unique..."
          rows={3}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
          disabled={isLoading || isImproving}
        />
      </div>

      {/* Logo Style */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Logo Style *
        </label>
        <div className="grid grid-cols-3 gap-2">
          {LOGO_STYLES.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              onClick={() => setStyle(value)}
              disabled={isLoading || isImproving}
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

      {/* Advanced Options Toggle */}
      <div>
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center gap-2"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Options
        </button>
      </div>

      {showAdvanced && (
        <div className="space-y-6 pt-4 border-t border-gray-200">
          {/* Size Selection - #33 */}
          <div>
            <label htmlFor="size" className="block text-sm font-medium text-gray-700 mb-2">
              Size & Dimensions
            </label>
            <select
              id="size"
              value={size}
              onChange={(e) => setSize(e.target.value as LogoSize)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              disabled={isLoading || isImproving}
            >
              {LOGO_SIZES.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Resolution Selection - #33 */}
          <div>
            <label htmlFor="resolution" className="block text-sm font-medium text-gray-700 mb-2">
              Resolution Quality
            </label>
            <select
              id="resolution"
              value={resolution}
              onChange={(e) => setResolution(e.target.value as LogoResolution)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              disabled={isLoading || isImproving}
            >
              {LOGO_RESOLUTIONS.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Filters & Effects - #34 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Visual Effects (Select multiple)
            </label>
            <div className="grid grid-cols-4 gap-2">
              {LOGO_FILTERS.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => toggleFilter(value)}
                  disabled={isLoading || isImproving}
                  className={`px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                    selectedFilters.includes(value)
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Transparency Toggle - #36 */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="transparency"
              checked={transparency}
              onChange={(e) => setTransparency(e.target.checked)}
              disabled={isLoading || isImproving}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <label htmlFor="transparency" className="text-sm font-medium text-gray-700">
              Enable Transparency (PNG with transparent background)
            </label>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        {/* AI Prompt Improver - #37 */}
        <button
          type="button"
          onClick={handleImprovePrompt}
          disabled={isLoading || isImproving || !businessName.trim()}
          className="flex-1 py-3 px-6 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isImproving ? '✨ Improving...' : '✨ AI Improve'}
        </button>

        {/* Quick Preview - #35 */}
        <button
          type="button"
          onClick={handlePreview}
          disabled={isLoading || isImproving || !businessName.trim()}
          className="flex-1 py-3 px-6 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '👁️ Previewing...' : '👁️ Quick Preview'}
        </button>

        {/* Generate Full Resolution */}
        <button
          type="submit"
          disabled={isLoading || isImproving || !businessName.trim()}
          className="flex-1 py-3 px-6 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '🎨 Generating...' : '🎨 Generate Logo'}
        </button>
      </div>

      <p className="text-xs text-gray-500 text-center">
        * Required fields
      </p>
    </form>
  );
};