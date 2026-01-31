import { clsx } from 'clsx';
import type { Style, StylePreset } from '../types';

interface StyleSelectorProps {
  styles: Style[];
  selectedStyle: StylePreset | null;
  onSelectStyle: (style: StylePreset | null) => void;
  disabled?: boolean;
}

export function StyleSelector({
  styles,
  selectedStyle,
  onSelectStyle,
  disabled = false,
}: StyleSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Style Preset <span className="text-gray-400">(optional)</span>
      </label>
      <div className="flex flex-wrap gap-2">
        {styles.map((style) => (
          <button
            key={style.id}
            type="button"
            disabled={disabled}
            onClick={() =>
              onSelectStyle(selectedStyle === style.id ? null : style.id)
            }
            className={clsx(
              'px-4 py-2 rounded-full text-sm font-medium transition-all',
              'border-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
              selectedStyle === style.id
                ? 'border-indigo-600 bg-indigo-600 text-white'
                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
            title={style.description}
          >
            {style.name}
          </button>
        ))}
      </div>
      {selectedStyle && (
        <p className="text-sm text-gray-500">
          {styles.find((s) => s.id === selectedStyle)?.description}
        </p>
      )}
    </div>
  );
}
