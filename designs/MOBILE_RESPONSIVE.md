# Mobile & Responsive Design

**Document:** Responsive Design Specifications
**Date:** 2026-01-30
**Designer:** Pixel 🎨

---

## Overview

This document defines the responsive behavior of the Logo Creator interface across all device sizes, ensuring a consistent and optimized user experience on mobile, tablet, and desktop.

---

## Breakpoints

```css
/* Mobile First Approach */
:root {
  --breakpoint-mobile: 320px;   /* Minimum supported */
  --breakpoint-tablet: 768px;   /* Tablet and up */
  --breakpoint-desktop: 1280px; /* Desktop and up */
  --breakpoint-large: 1920px;   /* Large screens */
}

/* Media Queries */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1280px) { /* Desktop */ }
@media (min-width: 1920px) { /* Large Desktop */ }
```

---

## 1. Mobile Layout (< 768px)

### Layout Structure

```
┌───────────────────────────────┐
│  ☰  Logo Creator      [Menu]  │ ← Sticky header (64px)
├───────────────────────────────┤
│                               │
│  ┌─────────────────────────┐  │
│  │ Prompt Input            │  │ ← Full width
│  │                         │  │
│  │ Describe your logo...   │  │
│  └─────────────────────────┘  │
│                               │
│  Style:                       │
│  ┌─────┐┌─────┐┌─────┐       │ ← Horizontal scroll
│  │ Min ││ Bld ││ Ply │ →     │   with snap
│  └─────┘└─────┘└─────┘       │
│                               │
│  ┌───────────────────────┐   │
│  │  ✨  Generate Logo   │   │ ← Full width button
│  └───────────────────────┘   │
│                               │
│  ┌─────────────────────────┐  │
│  │                         │  │
│  │      [Logo Preview]     │  │ ← Square, full width
│  │                         │  │
│  │    Zoom: + - ⟲         │  │
│  └─────────────────────────┘  │
│                               │
│  ┌───────────────────────┐   │
│  │ ⬇ Download PNG        │   │ ← Sticky bottom
│  └───────────────────────┘   │
│                               │
└───────────────────────────────┘
     ↑
History drawer (swipe up from bottom)
```

### Key Changes from Desktop

1. **Single Column Layout**
   - No sidebar history panel
   - All content stacks vertically
   - Full-width components

2. **Collapsed History**
   - History in bottom drawer
   - Swipe up to open
   - Overlay on content

3. **Sticky Elements**
   - Header sticks to top
   - Download button sticks to bottom (when logo generated)

4. **Touch Optimizations**
   - Minimum 44px touch targets
   - Larger padding and gaps
   - Swipe gestures enabled

---

### Mobile Header

```css
.header-mobile {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #1a1a2e;
  border-bottom: 1px solid #2a3f5f;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
}

.header-menu-button {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-toggle {
  /* Hamburger icon for history drawer */
  width: 24px;
  height: 24px;
  color: #ffffff;
}
```

---

### Mobile Prompt Input

```css
.prompt-input-mobile {
  width: 100%;
  min-height: 100px;
  padding: 16px;
  font-size: 16px; /* Prevent zoom on iOS */
  border-radius: 8px;
  margin: 16px 0;
}
```

**iOS Specific Fix:**
```css
/* Prevent iOS zoom on input focus */
@supports (-webkit-touch-callout: none) {
  input, textarea {
    font-size: 16px !important;
  }
}
```

---

### Mobile Style Selector

```css
.style-selector-mobile {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-snap-type: x mandatory;
  padding: 0 16px 16px 16px;
  margin: 0 -16px; /* Negative margin for edge-to-edge scroll */

  /* Hide scrollbar */
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.style-selector-mobile::-webkit-scrollbar {
  display: none;
}

.style-card-mobile {
  min-width: 120px;
  width: 120px;
  height: 120px;
  scroll-snap-align: center;
  scroll-snap-stop: always;
}

/* Show scroll indicator */
.style-selector-mobile::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 32px;
  background: linear-gradient(to right, transparent, #1a1a2e);
  pointer-events: none;
}
```

---

### Mobile Generate Button

```css
.generate-button-mobile {
  width: calc(100% - 32px);
  margin: 16px;
  height: 56px;
  font-size: 18px;

  /* Ensure touch target */
  min-height: 44px;
  padding: 12px 24px;
}
```

---

### Mobile Preview Panel

```css
.preview-panel-mobile {
  width: calc(100% - 32px);
  margin: 16px;
  aspect-ratio: 1 / 1; /* Force square */
  max-height: calc(100vw - 32px); /* Prevent overflow */
}

.preview-zoom-controls-mobile {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
}

.zoom-button-mobile {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #1e2d4d;
  border: 1px solid #2a3f5f;

  /* Touch feedback */
  -webkit-tap-highlight-color: rgba(108, 92, 231, 0.3);
}
```

---

### Mobile Download Button (Sticky)

```css
.download-button-mobile {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  height: 64px;
  border-radius: 0;
  border-top: 2px solid #6c5ce7;
  background: #16213e;
  z-index: 90;

  /* Safe area for iOS notch */
  padding-bottom: env(safe-area-inset-bottom);
}
```

---

### History Drawer (Mobile)

**Visual:**
```
┌─────────────────────────────┐
│                             │
│    Main content area        │
│                             │
│                             │
└─────────────────────────────┘
       ↑ Swipe up
┌─────────────────────────────┐
│         ───                 │ ← Drag handle
│  Recent Generations         │
│  ┌────┐  ┌────┐  ┌────┐    │
│  │ 1  │  │ 2  │  │ 3  │    │
│  └────┘  └────┘  └────┘    │
│  ┌────┐  ┌────┐  ┌────┐    │
│  │ 4  │  │ 5  │  │ 6  │    │
│  └────┘  └────┘  └────┘    │
└─────────────────────────────┘
```

**Implementation:**
```css
.history-drawer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60vh;
  max-height: 500px;
  background: #16213e;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  transform: translateY(100%);
  transition: transform 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
  z-index: 101;
  overflow-y: auto;
  padding-bottom: env(safe-area-inset-bottom);
}

.history-drawer.open {
  transform: translateY(0);
}

.drawer-handle {
  width: 40px;
  height: 4px;
  background: #6b7280;
  border-radius: 2px;
  margin: 12px auto;
}

.drawer-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 46, 0.8);
  z-index: 100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 300ms;
}

.drawer-backdrop.visible {
  opacity: 1;
  pointer-events: auto;
}
```

**Swipe Gesture (JavaScript):**
```javascript
let startY = 0;
let currentY = 0;

const handleTouchStart = (e) => {
  startY = e.touches[0].clientY;
};

const handleTouchMove = (e) => {
  currentY = e.touches[0].clientY;
  const diff = startY - currentY;

  // Swipe up to open
  if (diff > 50 && !isDrawerOpen) {
    openDrawer();
  }

  // Swipe down to close
  if (diff < -50 && isDrawerOpen) {
    closeDrawer();
  }
};
```

---

## 2. Tablet Layout (768px - 1279px)

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│  ☰  Logo Creator                        [Menu]  │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │ Prompt Input (full width, centered)    │    │
│  └────────────────────────────────────────┘    │
│                                                 │
│  Style: [Min] [Bold] [Play] [Prof] [Vint] [Mod]│
│                                                 │
│  ┌─────────────────────────┐                   │
│  │  ✨  Generate Logo      │                   │
│  └─────────────────────────┘                   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │                                         │   │
│  │         Logo Preview (wide)             │   │
│  │                                         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  ⬇  Download PNG (1024×1024)           │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Key Changes

1. **History remains in drawer** (same as mobile)
2. **Single column** but wider
3. **All 6 style cards visible** (no scrolling)
4. **Preview is wider** (16:9 or similar)
5. **Larger touch targets** maintained

**CSS:**
```css
@media (min-width: 768px) and (max-width: 1279px) {
  .container {
    max-width: 768px;
    margin: 0 auto;
    padding: 32px;
  }

  .style-selector {
    overflow-x: visible; /* All cards fit */
    gap: 16px;
  }

  .style-card {
    width: 110px;
    height: 110px;
  }

  .preview-panel {
    aspect-ratio: 16 / 9; /* Wider preview */
    max-width: 100%;
  }
}
```

---

## 3. Desktop Layout (1280px - 1919px)

### Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│  Logo Creator                                        [Menu]   │
├────────┬──────────────────────────────┬─────────────────────┤
│        │                              │                     │
│ Recent │  Prompt Input (centered)     │  Logo Preview       │
│ Gens   │                              │  (square)           │
│        │  Style: [6 cards]            │                     │
│ [Logo1]│                              │  [Generated Logo]   │
│ [Logo2]│  [Generate Button]           │                     │
│ [Logo3]│                              │  Zoom: [+ - ⟲]      │
│ ...    │                              │                     │
│        │                              │  [Download Button]  │
└────────┴──────────────────────────────┴─────────────────────┘
```

**Standard 3-column grid from main mockup.**

```css
@media (min-width: 1280px) {
  .layout-grid {
    display: grid;
    grid-template-columns: 240px 1fr minmax(400px, 40%);
    gap: 32px;
    height: calc(100vh - 80px);
  }

  .history-panel {
    display: block; /* Show sidebar */
  }

  .history-drawer {
    display: none; /* Hide drawer */
  }

  .preview-panel {
    aspect-ratio: 1 / 1; /* Square */
  }
}
```

---

## 4. Large Desktop (≥ 1920px)

### Layout Structure

Same as desktop, but with:
- Max container width: 1920px
- Centered layout
- Increased spacing

```css
@media (min-width: 1920px) {
  .layout-grid {
    max-width: 1920px;
    margin: 0 auto;
    grid-template-columns: 280px 1fr 600px;
    gap: 48px;
  }

  .prompt-input {
    max-width: 900px;
  }
}
```

---

## 5. Component Responsive Behavior

### Prompt Input

| Breakpoint | Height | Font Size | Padding |
|------------|--------|-----------|---------|
| Mobile | 100px | 16px | 16px |
| Tablet | 110px | 16px | 20px |
| Desktop | 120px | 16px | 20px |

### Style Cards

| Breakpoint | Size | Gap | Scroll |
|------------|------|-----|--------|
| Mobile | 120×120px | 12px | Yes (snap) |
| Tablet | 110×110px | 16px | No (all visible) |
| Desktop | 140×140px | 16px | No (all visible) |

### Generate Button

| Breakpoint | Width | Height |
|------------|-------|--------|
| Mobile | Full width | 56px |
| Tablet | 300px (centered) | 56px |
| Desktop | 300px (centered) | 56px |

### Preview Panel

| Breakpoint | Aspect Ratio | Max Size |
|------------|--------------|----------|
| Mobile | 1:1 | 100vw - 32px |
| Tablet | 16:9 | 100% |
| Desktop | 1:1 | 600px |

---

## 6. Touch Interactions

### Minimum Touch Targets

All interactive elements on mobile:
- **Minimum:** 44px × 44px (iOS Human Interface Guidelines)
- **Recommended:** 48px × 48px (Material Design)

### Touch Feedback

```css
/* Visual feedback on tap */
.interactive-element {
  -webkit-tap-highlight-color: rgba(108, 92, 231, 0.2);
  touch-action: manipulation; /* Disable double-tap zoom */
}

.interactive-element:active {
  transform: scale(0.98);
  transition: transform 100ms;
}
```

### Gestures

**Supported:**
- ✅ Tap to select
- ✅ Swipe to scroll (style selector)
- ✅ Swipe up/down (history drawer)
- ✅ Pinch to zoom (preview, optional)

**Not supported:**
- ❌ Complex multi-finger gestures
- ❌ Long press (conflicts with native behavior)

---

## 7. Safe Areas (iOS)

### iPhone Notch & Home Indicator

```css
/* Add safe area padding */
.header {
  padding-top: env(safe-area-inset-top);
}

.download-button-mobile {
  padding-bottom: env(safe-area-inset-bottom);
}

/* Full safe area support */
body {
  padding: env(safe-area-inset-top)
          env(safe-area-inset-right)
          env(safe-area-inset-bottom)
          env(safe-area-inset-left);
}
```

### Viewport Meta Tag

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
```

---

## 8. Performance Optimizations

### Mobile-Specific

1. **Lazy Load Images**
```javascript
<img
  src={logoUrl}
  loading="lazy"
  alt="Generated logo"
/>
```

2. **Reduce Animations on Low-End Devices**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

3. **Optimize Touch Scrolling**
```css
.scrollable-area {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}
```

---

## 9. Orientation Handling

### Portrait (Default)

Standard layouts as described above.

### Landscape (Mobile)

```css
@media (max-width: 767px) and (orientation: landscape) {
  .header {
    height: 56px; /* Reduce header */
  }

  .prompt-input {
    min-height: 80px; /* Reduce input */
  }

  .preview-panel {
    max-height: 60vh; /* Limit preview height */
  }

  /* Consider side-by-side layout */
  .content-area {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
}
```

---

## 10. Testing Matrix

### Devices to Test

| Device | Viewport | Priority |
|--------|----------|----------|
| iPhone SE | 375×667px | High |
| iPhone 12/13/14 | 390×844px | High |
| iPhone 14 Pro Max | 430×932px | Medium |
| iPad Mini | 768×1024px | High |
| iPad Pro | 1024×1366px | Medium |
| Desktop 1080p | 1920×1080px | High |
| Desktop 1440p | 2560×1440px | Medium |

### Test Checklist

**Mobile:**
- [ ] Header is sticky
- [ ] Prompt input doesn't zoom on focus (iOS)
- [ ] Style selector scrolls smoothly with snap
- [ ] History drawer opens/closes with swipe
- [ ] Download button is sticky (when logo exists)
- [ ] Touch targets are minimum 44px
- [ ] Safe areas respected (notch, home indicator)

**Tablet:**
- [ ] All style cards visible without scrolling
- [ ] Preview scales appropriately
- [ ] History drawer works
- [ ] Layout doesn't break at breakpoint transitions

**Desktop:**
- [ ] 3-column layout displays correctly
- [ ] History sidebar is visible
- [ ] History drawer is hidden
- [ ] All interactions work with mouse

**Cross-Device:**
- [ ] Fonts are readable at all sizes
- [ ] Colors have sufficient contrast
- [ ] Animations are smooth (60fps)
- [ ] Loading states work consistently
- [ ] Error states are visible and clear

---

## 11. Progressive Web App (PWA) Considerations

### Manifest.json

```json
{
  "name": "Logo Creator",
  "short_name": "LogoGen",
  "description": "AI-powered logo generator",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#6c5ce7",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### Install Prompt (Optional)

```css
.install-prompt {
  position: fixed;
  bottom: 80px;
  left: 16px;
  right: 16px;
  background: #16213e;
  border: 2px solid #6c5ce7;
  border-radius: 12px;
  padding: 16px;
  z-index: 200;
}
```

---

## 12. Implementation Priority

**Phase 1: Mobile Foundation**
1. Mobile-first CSS structure
2. Single column layout
3. Touch-optimized components
4. Basic responsive breakpoints

**Phase 2: Tablet Support**
5. Tablet breakpoint adjustments
6. Optimized style selector (all visible)
7. Wider preview layout

**Phase 3: Desktop Layout**
8. 3-column grid implementation
9. Sidebar history panel
10. Desktop-specific interactions

**Phase 4: Enhancements**
11. History drawer with gestures
12. Advanced animations
13. PWA features (optional)
14. Orientation handling

---

**Designer:** Pixel 🎨
**Document:** Mobile & Responsive Design
**Date:** 2026-01-30
**Status:** Ready for Implementation
