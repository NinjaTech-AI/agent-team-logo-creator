# Component Design: Style Selector

**Component:** Style Selector
**Date:** 2026-01-30
**Designer:** Pixel 🎨

---

## Component Overview

The Style Selector allows users to choose from 6 predefined logo styles: Minimal, Bold, Playful, Professional, Vintage, and Modern. It uses a visual card-based interface with icons and labels for easy recognition.

---

## Visual Design

### Desktop Layout (Full Width Available)
```
Style: ← Label (16px Inter Bold, #ffffff, margin-bottom: 12px)

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│          │ │          │ │          │ │          │ │          │ │          │
│    ○     │ │    ◢◣    │ │    ☺     │ │    ▦     │ │    ♕     │ │    ⌇     │
│   ╱│╲    │ │   ████   │ │   (◠◡◠)  │ │   ╱│╲    │ │  ╭───╮   │ │   ╱ ╲    │
│          │ │   ████   │ │          │ │  ─┼─┼─   │ │  │ ♕ │   │ │  ╱   ╲   │
│ Minimal  │ │   Bold   │ │ Playful  │ │   ╲│╱    │ │  ╰───╯   │ │  Modern  │
│          │ │          │ │          │ │Professional│ │ Vintage  │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
 140x140px    140x140px    140x140px    140x140px    140x140px    140x140px
```

### Mobile Layout (Horizontal Scroll)
```
← Swipe to see more styles →

┌──────────┐ ┌──────────┐ ┌──────────┐
│          │ │          │ │          │
│    ○     │ │    ◢◣    │ │    ☺     │
│   ╱│╲    │ │   ████   │ │   (◠◡◠)  │
│          │ │   ████   │ │          │
│ Minimal  │ │   Bold   │ │ Playful  │
│          │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘
```

---

## Technical Specifications

### Container
```css
.style-selector {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  padding-bottom: 8px; /* For scroll bar space */

  /* Hide scrollbar but keep functionality */
  scrollbar-width: thin;
  scrollbar-color: #6c5ce7 #1a1a2e;
}

/* Webkit browsers */
.style-selector::-webkit-scrollbar {
  height: 6px;
}

.style-selector::-webkit-scrollbar-track {
  background: #1a1a2e;
  border-radius: 3px;
}

.style-selector::-webkit-scrollbar-thumb {
  background: #6c5ce7;
  border-radius: 3px;
}

.style-selector::-webkit-scrollbar-thumb:hover {
  background: #8b7ee8;
}
```

### Style Card
```css
.style-card {
  /* Size */
  width: 140px;
  height: 140px;
  min-width: 140px; /* Prevent shrinking */

  /* Layout */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;

  /* Styling */
  background: #16213e;
  border: 2px solid #2a3f5f;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;

  /* Transition */
  transition: all 150ms cubic-bezier(0.4, 0.0, 0.2, 1);

  /* Interaction */
  user-select: none;
}

/* Hover State */
.style-card:hover {
  border-color: #6c5ce7;
  transform: scale(1.02);
}

.style-card:hover .style-icon {
  opacity: 1;
}

.style-card:hover .style-label {
  opacity: 1;
}

/* Active/Pressed State */
.style-card:active {
  transform: scale(0.98);
}

/* Selected State */
.style-card.selected {
  border-color: #6c5ce7;
  background: #1e2d4d;
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.style-card.selected .style-icon {
  opacity: 1;
}

.style-card.selected .style-label {
  opacity: 1;
}
```

### Icon Container
```css
.style-icon {
  /* Size */
  width: 80px;
  height: 80px;

  /* Layout */
  display: flex;
  align-items: center;
  justify-content: center;

  /* Styling */
  opacity: 0.7;
  transition: opacity 150ms;
}

.style-icon svg {
  width: 100%;
  height: 100%;
  fill: #ffffff;
  stroke: #ffffff;
}
```

### Label
```css
.style-label {
  /* Typography */
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 16px;
  line-height: 20px;
  color: #ffffff;

  /* Styling */
  text-align: center;
  opacity: 0.7;
  transition: opacity 150ms;

  /* Prevent text selection */
  user-select: none;
}
```

---

## Style Definitions

### 1. Minimal
**Philosophy:** Clean, simple, less is more
**Visual Elements:** Simple geometric shapes, thin lines, lots of white space
**Icon Design:**
```
    ○         ← Simple circle outline
   ╱│╲        ← Single vertical line with minimal branches
```
**SVG Icon Code:**
```svg
<svg width="80" height="80" viewBox="0 0 80 80" fill="none">
  <circle cx="40" cy="30" r="12" stroke="currentColor" stroke-width="2"/>
  <line x1="40" y1="42" x2="40" y2="60" stroke="currentColor" stroke-width="2"/>
  <line x1="30" y1="55" x2="50" y2="55" stroke="currentColor" stroke-width="2"/>
</svg>
```

### 2. Bold
**Philosophy:** Strong, impactful, confident
**Visual Elements:** Thick lines, solid shapes, heavy weight, high contrast
**Icon Design:**
```
    ◢◣        ← Thick triangle top
   ████       ← Solid filled shape
   ████       ← Strong, heavy appearance
```
**SVG Icon Code:**
```svg
<svg width="80" height="80" viewBox="0 0 80 80" fill="currentColor">
  <polygon points="40,20 55,35 55,60 25,60 25,35"/>
  <rect x="25" y="55" width="30" height="10" rx="2"/>
</svg>
```

### 3. Playful
**Philosophy:** Fun, friendly, approachable
**Visual Elements:** Rounded shapes, whimsical elements, cheerful characters
**Icon Design:**
```
    ☺         ← Happy face
   (◠◡◠)      ← Rounded, friendly character
```
**SVG Icon Code:**
```svg
<svg width="80" height="80" viewBox="0 0 80 80" fill="none">
  <circle cx="40" cy="40" r="20" stroke="currentColor" stroke-width="3"/>
  <circle cx="33" cy="35" r="2" fill="currentColor"/>
  <circle cx="47" cy="35" r="2" fill="currentColor"/>
  <path d="M 30 45 Q 40 50 50 45" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
```

### 4. Professional
**Philosophy:** Corporate, trustworthy, balanced
**Visual Elements:** Structured grids, symmetrical, clean divisions
**Icon Design:**
```
    ▦         ← Structured grid
   ╱│╲        ← Balanced, symmetrical
  ─┼─┼─       ← Professional divisions
   ╲│╱
```
**SVG Icon Code:**
```svg
<svg width="80" height="80" viewBox="0 0 80 80" fill="none">
  <rect x="25" y="25" width="30" height="30" stroke="currentColor" stroke-width="2"/>
  <line x1="40" y1="25" x2="40" y2="55" stroke="currentColor" stroke-width="2"/>
  <line x1="25" y1="40" x2="55" y2="40" stroke="currentColor" stroke-width="2"/>
</svg>
```

### 5. Vintage
**Philosophy:** Classic, timeless, nostalgic
**Visual Elements:** Badge shapes, ornate details, retro typography
**Icon Design:**
```
    ♕         ← Crown/classic emblem
  ╭───╮       ← Badge/shield shape
  │ ♕ │       ← Ornate center element
  ╰───╯
```
**SVG Icon Code:**
```svg
<svg width="80" height="80" viewBox="0 0 80 80" fill="none">
  <path d="M 30 25 L 40 20 L 50 25 L 55 45 Q 55 55 40 60 Q 25 55 25 45 Z"
        stroke="currentColor" stroke-width="2"/>
  <circle cx="40" cy="38" r="5" stroke="currentColor" stroke-width="2"/>
  <path d="M 35 30 L 40 25 L 45 30" stroke="currentColor" stroke-width="2" fill="none"/>
</svg>
```

### 6. Modern
**Philosophy:** Contemporary, sleek, forward-thinking
**Visual Elements:** Abstract curves, gradients, asymmetric balance
**Icon Design:**
```
    ⌇         ← Abstract curve
   ╱ ╲        ← Sleek, flowing lines
  ╱   ╲       ← Dynamic shape
```
**SVG Icon Code:**
```svg
<svg width="80" height="80" viewBox="0 0 80 80" fill="none">
  <path d="M 25 55 Q 35 25 45 45 T 55 25"
        stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <circle cx="45" cy="45" r="8" stroke="currentColor" stroke-width="2"/>
</svg>
```

---

## Interactive Behavior

### Selection Logic
```javascript
// React component example
const [selectedStyle, setSelectedStyle] = useState(null);

const handleStyleSelect = (styleId) => {
  setSelectedStyle(styleId);
  // Trigger parent callback
  onStyleChange(styleId);
};

const styles = [
  { id: 'minimal', name: 'Minimal', icon: MinimalIcon },
  { id: 'bold', name: 'Bold', icon: BoldIcon },
  { id: 'playful', name: 'Playful', icon: PlayfulIcon },
  { id: 'professional', name: 'Professional', icon: ProfessionalIcon },
  { id: 'vintage', name: 'Vintage', icon: VintageIcon },
  { id: 'modern', name: 'Modern', icon: ModernIcon },
];
```

### Keyboard Navigation
- **Tab:** Focus moves to style selector
- **Arrow Left/Right:** Navigate between style cards
- **Enter/Space:** Select focused style card
- **Tab:** Exit to next focusable element (Generate button)

### Accessibility
```jsx
<div
  className={`style-card ${selectedStyle === style.id ? 'selected' : ''}`}
  role="radio"
  aria-checked={selectedStyle === style.id}
  tabIndex={selectedStyle === style.id ? 0 : -1}
  onClick={() => handleStyleSelect(style.id)}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleStyleSelect(style.id);
    }
  }}
>
  <div className="style-icon" aria-hidden="true">
    <style.icon />
  </div>
  <span className="style-label">{style.name}</span>
</div>
```

### Focus Management
```css
/* Keyboard focus indicator */
.style-card:focus {
  outline: 2px solid #6c5ce7;
  outline-offset: 2px;
}

.style-card:focus:not(:focus-visible) {
  outline: none;
}

.style-card:focus-visible {
  outline: 2px solid #6c5ce7;
  outline-offset: 2px;
}
```

---

## Responsive Behavior

### Desktop (≥1280px)
- All 6 cards visible in one row
- No scrolling needed
- Gap: 16px

### Tablet (768px - 1279px)
- Horizontal scroll enabled
- Cards maintain 140px size
- Snap scroll to each card
- Show scroll hint (fade on edges)

### Mobile (<768px)
- Horizontal scroll with snap
- Show 2.5 cards at once (hint at more)
- Larger touch targets (48px minimum)
- Swipe gesture supported

```css
@media (max-width: 767px) {
  .style-selector {
    /* Snap scrolling */
    scroll-snap-type: x mandatory;
    padding-left: 16px;
    padding-right: 16px;
  }

  .style-card {
    scroll-snap-align: center;
    scroll-snap-stop: always;
  }

  /* Show scroll hint with fade */
  .style-selector::after {
    content: '';
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 40px;
    background: linear-gradient(to right, transparent, #1a1a2e);
    pointer-events: none;
  }
}
```

---

## Animation Details

### Card Selection Animation
```css
@keyframes selectCard {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(0.95);
  }
  100% {
    transform: scale(1);
    border-color: #6c5ce7;
    box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
  }
}

.style-card.selected {
  animation: selectCard 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

### Icon Glow on Hover (Optional Enhancement)
```css
.style-card:hover .style-icon svg {
  filter: drop-shadow(0 0 8px rgba(108, 92, 231, 0.5));
  transition: filter 150ms;
}
```

---

## Error States

### No Style Selected
When user tries to generate without selecting a style:
```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️ Please select a style before generating                   │
└──────────────────────────────────────────────────────────────┘
```
- Show below style selector
- Background: rgba(239, 68, 68, 0.1)
- Border left: 4px solid #ef4444
- Padding: 12px 16px
- Border radius: 4px
- Auto-dismiss after 5 seconds

---

## Integration with Form

### React Component Structure
```jsx
<form onSubmit={handleGenerate}>
  <PromptInput
    value={prompt}
    onChange={setPrompt}
    placeholder="Describe your logo..."
  />

  <StyleSelector
    styles={AVAILABLE_STYLES}
    selected={selectedStyle}
    onSelect={setSelectedStyle}
  />

  <GenerateButton
    disabled={!prompt || !selectedStyle}
    loading={isGenerating}
  />
</form>
```

### Validation
```javascript
const canGenerate = () => {
  return prompt.trim().length >= 10 && selectedStyle !== null;
};
```

---

## Testing Checklist

- [ ] All 6 styles render correctly
- [ ] Only one style can be selected at a time
- [ ] Click toggles selection (or radio behavior)
- [ ] Hover state shows on all cards
- [ ] Selected state persists visually
- [ ] Keyboard navigation works (arrows, enter, space)
- [ ] Focus indicator visible for keyboard users
- [ ] Screen reader announces selection state
- [ ] Horizontal scroll works on mobile
- [ ] Snap scroll works correctly
- [ ] Icons load and display properly
- [ ] Responsive breakpoints adjust layout
- [ ] Touch targets are 44px minimum on mobile

---

## Assets Required

### Icon SVG Files
Create these files in `/designs/assets/style-icons/`:
- `minimal.svg` (80×80px)
- `bold.svg` (80×80px)
- `playful.svg` (80×80px)
- `professional.svg` (80×80px)
- `vintage.svg` (80×80px)
- `modern.svg` (80×80px)

### Icon Export Settings
- Format: SVG
- Size: 80×80px viewBox
- Stroke width: 2-3px
- Color: currentColor (inherits from CSS)
- Optimize: Remove unnecessary metadata

---

## Implementation Notes for Bolt ⚡

### Recommended Approach
1. Create reusable `StyleCard` component
2. Import icon SVGs as React components
3. Use radio group pattern for accessibility
4. Store selected style in parent form state
5. Validate selection before allowing form submit

### Libraries to Consider
- **Icons:** Custom SVG components (already designed above)
- **Scroll:** Native CSS scroll-snap (no library needed)
- **State:** React useState or form library (React Hook Form)

### Performance
- Icons are lightweight SVGs (< 1KB each)
- No images to load, instant render
- CSS transitions hardware-accelerated
- Minimal re-renders on selection

---

**Designer:** Pixel 🎨
**Component:** Style Selector
**Date:** 2026-01-30
**Status:** Ready for Implementation
