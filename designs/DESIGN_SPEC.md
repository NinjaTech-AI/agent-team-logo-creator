# Logo Creator - Design Specification

**Version:** 1.0
**Date:** 2026-01-30
**Designer:** Pixel 🎨

---

## Design Philosophy

The Logo Creator interface emphasizes clarity, creativity, and efficiency. The dark theme provides a professional canvas that makes generated logos pop, while the purple accent color adds a touch of creativity and innovation.

---

## Color System

### Primary Colors
```
Primary Purple:    #6c5ce7  (RGB: 108, 92, 231)
Primary Hover:     #5f4dd4  (Darker purple for interactions)
Primary Light:     #8b7ee8  (Lighter purple for accents)
```

### Background Colors
```
Background Dark:   #1a1a2e  (Main background)
Surface:          #16213e  (Cards, panels)
Surface Elevated: #1e2d4d  (Hover states, elevated elements)
Border:           #2a3f5f  (Dividers, borders)
```

### Text Colors
```
Text Primary:     #ffffff  (Headings, primary content)
Text Secondary:   #a0a0a0  (Descriptions, labels)
Text Tertiary:    #6b7280  (Placeholder text, hints)
```

### Status Colors
```
Success:          #10b981  (Generation complete)
Error:            #ef4444  (Generation failed)
Warning:          #f59e0b  (Warnings)
Info:             #3b82f6  (Info messages)
```

---

## Typography

### Font Families
```
Headings:         'Inter', sans-serif (Bold, 700)
Body:            'Inter', sans-serif (Regular, 400)
Monospace:       'JetBrains Mono', monospace (For prompts)
```

### Type Scale
```
Display:         48px / 60px line-height (Logo Creator title)
H1:              36px / 44px line-height (Page titles)
H2:              24px / 32px line-height (Section headers)
H3:              20px / 28px line-height (Component titles)
Body Large:      18px / 28px line-height (Primary content)
Body:            16px / 24px line-height (Standard text)
Body Small:      14px / 20px line-height (Labels, captions)
Caption:         12px / 16px line-height (Hints, metadata)
```

---

## Spacing System

Based on 8px grid:
```
xs:    4px
sm:    8px
md:    16px
lg:    24px
xl:    32px
2xl:   48px
3xl:   64px
```

---

## Component Specifications

### 1. Main Container
- **Width:** 100% with max-width 1920px
- **Padding:** 32px (desktop), 16px (mobile)
- **Background:** #1a1a2e

### 2. Prompt Input Area
- **Position:** Top center of interface
- **Width:** 100% max 800px
- **Height:** Auto (min 120px)
- **Background:** #16213e
- **Border:** 2px solid #2a3f5f
- **Border Radius:** 12px
- **Padding:** 20px
- **Font:** 16px JetBrains Mono
- **Placeholder:** "Describe your logo... (e.g., 'A modern tech company logo with a rocket')"

**States:**
- Default: Border #2a3f5f
- Focus: Border #6c5ce7, glow effect (0 0 0 3px rgba(108, 92, 231, 0.1))
- Error: Border #ef4444

### 3. Style Selector Component
- **Layout:** Horizontal scrollable grid
- **Item Size:** 140px × 140px
- **Gap:** 16px
- **Border Radius:** 8px
- **Background:** #16213e

**Style Cards:**
Each style card contains:
- Icon/visual representation (80px × 80px)
- Style name (16px, bold)
- Border: 2px solid #2a3f5f

**States:**
- Default: Border #2a3f5f, opacity 0.7
- Hover: Border #6c5ce7, opacity 1, scale(1.02)
- Selected: Border #6c5ce7, background #1e2d4d, glow effect

**Six Styles:**
1. Minimal - Clean lines, simple geometry
2. Bold - Strong, thick elements
3. Playful - Rounded, fun shapes
4. Professional - Corporate, balanced
5. Vintage - Classic, retro feel
6. Modern - Contemporary, sleek

### 4. Generate Button
- **Width:** 200px (auto on mobile)
- **Height:** 56px
- **Background:** Linear gradient (#6c5ce7 to #5f4dd4)
- **Border Radius:** 28px (fully rounded)
- **Font:** 18px Inter Bold
- **Text:** "Generate Logo"
- **Icon:** Sparkle/star icon (left side)

**States:**
- Default: Gradient background, white text
- Hover: Lift effect (translateY(-2px)), shadow increase
- Active: Scale(0.98)
- Loading: Spinning animation on icon, text "Generating..."
- Disabled: Opacity 0.5, cursor not-allowed

### 5. Logo Preview Panel
- **Position:** Center-right of interface
- **Width:** 60% of container (min 400px)
- **Aspect Ratio:** 1:1 (square)
- **Background:** #16213e
- **Border:** 2px solid #2a3f5f
- **Border Radius:** 16px
- **Padding:** 32px

**Preview Image:**
- Max width/height: 512px
- Centered in panel
- Drop shadow: 0 20px 40px rgba(0, 0, 0, 0.3)

**Zoom Controls:**
- Position: Bottom-right of panel
- Buttons: Zoom in (+), Zoom out (-), Reset (⟲)
- Size: 40px × 40px each
- Background: #1e2d4d
- Border radius: 8px

### 6. Download Button
- **Position:** Below preview panel
- **Width:** 100% of preview panel
- **Height:** 48px
- **Background:** #16213e
- **Border:** 2px solid #6c5ce7
- **Border Radius:** 8px
- **Font:** 16px Inter Bold
- **Text:** "Download PNG (1024×1024)"
- **Icon:** Download icon (left side)

**States:**
- Default: Border #6c5ce7, text #6c5ce7
- Hover: Background #6c5ce7, text white
- Disabled: Opacity 0.5 (when no logo generated)

### 7. History Panel
- **Position:** Left sidebar
- **Width:** 240px (desktop), full width drawer (mobile)
- **Background:** #16213e
- **Border Right:** 1px solid #2a3f5f
- **Padding:** 16px

**Title:**
- Text: "Recent Generations"
- Font: 18px Inter Bold
- Margin bottom: 16px

**History Grid:**
- Layout: Vertical list
- Item size: 100% × 80px
- Gap: 12px
- Max items: 10

**History Item:**
- Background: #1a1a2e
- Border: 2px solid transparent
- Border radius: 8px
- Padding: 8px
- Display: Thumbnail (60px × 60px) + prompt preview

**States:**
- Default: Border transparent
- Hover: Border #6c5ce7, cursor pointer
- Selected: Border #6c5ce7, background #1e2d4d

### 8. Loading State
**Full-screen overlay:**
- Background: rgba(26, 26, 46, 0.95)
- Z-index: 1000

**Loading Content:**
- Center-positioned spinner
- Spinner: Animated purple circle (60px diameter)
- Text: "Generating your logo..."
- Sub-text: "This may take a few seconds"
- Font: 18px / 14px

### 9. Error State
**Inline error (below input):**
- Background: rgba(239, 68, 68, 0.1)
- Border left: 4px solid #ef4444
- Padding: 12px 16px
- Border radius: 4px
- Icon: Alert circle (red)
- Text: Error message in red (#ef4444)

**Empty state (no history):**
- Center-aligned in history panel
- Icon: Image/sparkle icon (gray)
- Text: "No logos yet"
- Sub-text: "Your generated logos will appear here"

---

## Layout Specifications

### Desktop Layout (1920px)
```
┌─────────────────────────────────────────────────────────────┐
│                     Logo Creator Header                      │
│                                                               │
├──────────┬──────────────────────────────┬────────────────────┤
│          │                              │                    │
│ History  │   Prompt Input Area          │   Logo Preview     │
│ Panel    │   (centered, max 800px)      │   Panel            │
│ (240px)  │                              │   (60% width)      │
│          │   Style Selector             │                    │
│ - Item 1 │   (6 cards horizontal)       │   [Generated       │
│ - Item 2 │                              │    Logo Image]     │
│ - Item 3 │   [Generate Button]          │                    │
│ - Item 4 │                              │   Zoom Controls    │
│ ...      │                              │                    │
│          │                              │   [Download Btn]   │
│          │                              │                    │
└──────────┴──────────────────────────────┴────────────────────┘
```

### Tablet Layout (768px - 1279px)
- History panel collapses to drawer (icon button)
- Prompt and preview stack vertically
- Style selector remains horizontal scrollable
- Preview width: 100%

### Mobile Layout (<768px)
- Single column layout
- History: Bottom drawer
- Prompt: Full width
- Style selector: Horizontal scroll with snap
- Preview: Full width, square aspect ratio
- Download: Full width sticky bottom button

---

## Interaction Patterns

### 1. Logo Generation Flow
```
User enters prompt → Selects style → Clicks Generate
  ↓
Loading overlay appears with spinner
  ↓
Logo generates (3-5 seconds)
  ↓
Preview updates with fade-in animation
  ↓
Download button enables
  ↓
Logo added to history (top of list)
```

### 2. Style Selection
- Click to select (radio button behavior)
- Only one style active at a time
- Visual feedback with border color change
- Hover effect on all styles

### 3. History Interaction
- Click item to load logo in preview
- Hover shows full prompt as tooltip
- Auto-scroll to top when new item added
- Max 10 items (oldest removed automatically)

### 4. Preview Zoom
- Click zoom in/out buttons
- Zoom levels: 50%, 75%, 100%, 125%, 150%, 200%
- Reset button returns to 100%
- Draggable when zoomed

---

## Accessibility

### Color Contrast
- Text on background meets WCAG AA (4.5:1 minimum)
- Primary button meets WCAG AAA (7:1)
- Error states clearly distinguishable

### Keyboard Navigation
- Tab order: Prompt → Style cards → Generate → Preview controls → Download → History
- Enter/Space to activate buttons
- Arrow keys to navigate style selector
- Escape to close modals/drawers

### Screen Readers
- Alt text for all images
- ARIA labels for icon buttons
- Live regions for loading/error states
- Semantic HTML structure

### Focus States
- Visible focus ring: 2px solid #6c5ce7, offset 2px
- Focus ring on all interactive elements
- Skip to content link for keyboard users

---

## Animations & Transitions

### Timing
```
Fast:       150ms  (Hover effects, button states)
Normal:     300ms  (Panel openings, content transitions)
Slow:       500ms  (Page loads, large content changes)
```

### Easing
```
Standard:   cubic-bezier(0.4, 0.0, 0.2, 1)  (Most transitions)
Decelerate: cubic-bezier(0.0, 0.0, 0.2, 1)  (Entering elements)
Accelerate: cubic-bezier(0.4, 0.0, 1, 1)    (Exiting elements)
```

### Key Animations
1. **Logo Fade-in:** opacity 0 → 1, scale 0.95 → 1 (500ms)
2. **Button Hover:** translateY(0) → translateY(-2px) (150ms)
3. **Loading Spinner:** rotate 360deg infinite (1s linear)
4. **History Add:** slideInDown + fade (300ms)
5. **Error Shake:** translateX(-5px, 5px, -5px, 0) (400ms)

---

## Responsive Breakpoints

```
Mobile:       < 768px
Tablet:       768px - 1279px
Desktop:      1280px - 1919px
Large:        ≥ 1920px
```

### Responsive Rules
- Font sizes scale down 10-20% on mobile
- Touch targets minimum 44px × 44px
- Spacing reduces by 25-50% on mobile
- Horizontal scrolling for style selector on mobile
- Sticky header on scroll (mobile/tablet)

---

## Design Assets

### Required Icons (24px, #ffffff)
- Sparkle/Star (Generate button)
- Download (Download button)
- Zoom In (+)
- Zoom Out (-)
- Reset (⟲)
- Menu (History drawer toggle)
- Alert Circle (Errors)
- Info Circle (Info messages)
- Close (X) (Modals/drawers)

### Style Icons (80px × 80px)
Each style needs a representative icon/illustration:
1. Minimal - Simple circle with line
2. Bold - Thick geometric shape
3. Playful - Rounded character/mascot
4. Professional - Clean corporate symbol
5. Vintage - Retro badge/emblem
6. Modern - Abstract sleek shape

---

## Implementation Notes for Bolt ⚡

### Priority Components (Build Order)
1. Main layout structure with responsive grid
2. Prompt input with focus states
3. Style selector component with selection logic
4. Generate button with loading states
5. Preview panel with placeholder
6. Download functionality
7. History panel with storage
8. Zoom/pan controls
9. Error handling UI
10. Mobile responsive adjustments

### Suggested Libraries
- **Styling:** Tailwind CSS (already in stack)
- **Animations:** Framer Motion or CSS transitions
- **Icons:** Lucide React or Heroicons
- **State:** React Context or Zustand (for history)
- **Image Zoom:** react-zoom-pan-pinch (optional)

### Critical Implementation Details
- Use CSS Grid for main layout (not Flexbox)
- Preview panel aspect ratio maintained with `aspect-square`
- History stored in localStorage (session-based)
- Responsive design mobile-first approach
- Loading overlay blocks UI interaction
- Form validation before API call

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-30 | Initial design specification created by Pixel |

---

**Designer:** Pixel 🎨
**Contact:** @pixel in #logo-creator
**Repository:** NinjaTech-AI/agent-team-logo-creator
