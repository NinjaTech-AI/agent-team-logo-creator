# Main Interface Mockup - Desktop View

**Component:** Logo Creator - Main Interface
**Resolution:** 1920px × 1080px
**Date:** 2026-01-30
**Designer:** Pixel 🎨

---

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Logo Creator                                                    [User Menu] │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                               │
│  ┌───────────┬───────────────────────────────────┬─────────────────────────┐│
│  │           │                                   │                         ││
│  │ Recent    │     ┌─────────────────────┐      │   ┌─────────────────┐   ││
│  │ Gens      │     │  Prompt Input Area  │      │   │                 │   ││
│  │           │     │                     │      │   │                 │   ││
│  │ ┌───────┐ │     │ Describe your logo  │      │   │   Generated     │   ││
│  │ │ Logo1 │ │     │ ...                 │      │   │   Logo          │   ││
│  │ │       │ │     │                     │      │   │   Preview       │   ││
│  │ └───────┘ │     │                     │      │   │                 │   ││
│  │           │     └─────────────────────┘      │   │                 │   ││
│  │ ┌───────┐ │                                  │   │   512x512       │   ││
│  │ │ Logo2 │ │     Style:                       │   │                 │   ││
│  │ │       │ │     ┌────┐┌────┐┌────┐┌────┐    │   │                 │   ││
│  │ └───────┘ │     │Min ││Bold││Play││Prof│    │   └─────────────────┘   ││
│  │           │     └────┘└────┘└────┘└────┘    │                         ││
│  │ ┌───────┐ │     ┌────┐┌────┐                │   ┌───┬───┬───┐         ││
│  │ │ Logo3 │ │     │Vint││Mdrn│                │   │ + │ - │ ⟲ │         ││
│  │ │       │ │     └────┘└────┘                │   └───┴───┴───┘         ││
│  │ └───────┘ │                                  │                         ││
│  │           │     ┌──────────────────┐         │   ┌─────────────────┐   ││
│  │           │     │ ✨ Generate Logo │         │   │ ⬇ Download PNG  │   ││
│  │           │     └──────────────────┘         │   │   (1024×1024)   │   ││
│  │           │                                  │   └─────────────────┘   ││
│  └───────────┴───────────────────────────────────┴─────────────────────────┘│
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Breakdown

### 1. Header
**Position:** Top of screen, full width
**Height:** 80px
**Background:** #1a1a2e
**Border Bottom:** 1px solid #2a3f5f

**Content:**
- Left: "Logo Creator" (32px Inter Bold, #ffffff)
- Right: User menu icon (if auth implemented)
- Padding: 0 32px

---

### 2. History Panel (Left Sidebar)
**Position:** Fixed left
**Width:** 240px
**Background:** #16213e
**Border Right:** 1px solid #2a3f5f
**Padding:** 16px

#### Panel Header
- Title: "Recent Generations" (18px Inter Bold, #ffffff)
- Margin bottom: 16px

#### History Items (Scrollable List)
Each item:
- **Size:** 208px × 80px (full width minus padding)
- **Background:** #1a1a2e
- **Border:** 2px solid transparent
- **Border Radius:** 8px
- **Padding:** 8px
- **Cursor:** pointer
- **Transition:** all 150ms

**Item Content:**
```
┌────────────────────────┐
│ ┌──────┐ Modern tech... │
│ │ [60] │ company logo   │
│ │      │ 2 mins ago     │
│ └──────┘               │
└────────────────────────┘
```
- Left: Thumbnail (60px × 60px, border-radius 4px)
- Right:
  - Prompt preview (14px, #ffffff, truncate to 2 lines)
  - Timestamp (12px, #6b7280)

**Item States:**
- Default: Border transparent, background #1a1a2e
- Hover: Border #6c5ce7, background #1e2d4d
- Selected: Border #6c5ce7, background #1e2d4d

**Empty State:**
```
┌────────────────────────┐
│                        │
│        ✧               │
│   No logos yet         │
│                        │
│   Your generated       │
│   logos will           │
│   appear here          │
│                        │
└────────────────────────┘
```
- Icon: Sparkle/star (48px, #6b7280)
- Text: 14px, #6b7280, centered

---

### 3. Main Content Area (Center)
**Position:** Between history and preview
**Width:** Flexible (calc(100% - 240px - preview width))
**Max Width:** 800px
**Padding:** 32px
**Centered horizontally**

#### 3a. Prompt Input Area
**Width:** 100%
**Min Height:** 120px
**Background:** #16213e
**Border:** 2px solid #2a3f5f
**Border Radius:** 12px
**Padding:** 20px
**Margin Bottom:** 24px

**Input Field:**
- Font: 16px JetBrains Mono, #ffffff
- Line height: 24px
- Placeholder: "Describe your logo... (e.g., 'A modern tech company logo with a rocket')"
- Placeholder color: #6b7280
- Resize: vertical
- Min height: 80px

**Focus State:**
- Border: 2px solid #6c5ce7
- Box shadow: 0 0 0 3px rgba(108, 92, 231, 0.1)
- Outline: none

**Character Count (Optional):**
- Position: Bottom right of input
- Text: "250/500" (12px, #6b7280)

#### 3b. Style Selector Section
**Margin Bottom:** 24px

**Section Header:**
- Text: "Style" (16px Inter Bold, #ffffff)
- Margin bottom: 12px

**Style Grid:**
- Layout: Horizontal flexbox with gap 16px
- Overflow: auto (horizontal scroll if needed)
- Scroll behavior: smooth

**Style Card (6 cards):**
```
┌──────────┐
│          │
│  [Icon]  │ ← 80px × 80px icon
│          │
│ Minimal  │ ← 16px Bold
└──────────┘
```
- Size: 140px × 140px
- Background: #16213e
- Border: 2px solid #2a3f5f
- Border radius: 8px
- Padding: 16px
- Display: flex column, center aligned
- Cursor: pointer
- Transition: all 150ms

**Icon Area:**
- Size: 80px × 80px
- Centered
- Margin bottom: 8px

**Label:**
- Font: 16px Inter Bold, #ffffff
- Text align: center
- Opacity: 0.7 (default), 1 (selected/hover)

**States:**
- Default: Border #2a3f5f, opacity 0.7
- Hover: Border #6c5ce7, opacity 1, transform scale(1.02)
- Selected: Border #6c5ce7, background #1e2d4d, box-shadow 0 0 0 3px rgba(108, 92, 231, 0.1)

**Six Styles:**
1. **Minimal** - Icon: Simple circle with single line
2. **Bold** - Icon: Thick geometric hexagon
3. **Playful** - Icon: Rounded happy face/mascot
4. **Professional** - Icon: Balanced square with division
5. **Vintage** - Icon: Classic badge/shield outline
6. **Modern** - Icon: Abstract sleek curved shape

#### 3c. Generate Button
**Width:** 100%
**Max Width:** 300px
**Height:** 56px
**Margin:** 0 auto (centered)
**Background:** linear-gradient(135deg, #6c5ce7 0%, #5f4dd4 100%)
**Border:** none
**Border Radius:** 28px
**Cursor:** pointer
**Transition:** all 150ms

**Button Content:**
```
┌──────────────────────┐
│  ✨  Generate Logo   │
└──────────────────────┘
```
- Icon: Sparkle (left, 20px)
- Text: "Generate Logo" (18px Inter Bold, #ffffff)
- Spacing: 8px between icon and text
- Justify: center, align: center

**States:**
- Default: Gradient background
- Hover: transform translateY(-2px), box-shadow 0 8px 16px rgba(108, 92, 231, 0.3)
- Active: transform scale(0.98)
- Loading:
  - Icon: Spinning animation (rotate 360deg, 1s infinite)
  - Text: "Generating..."
  - Cursor: not-allowed
- Disabled (no prompt or style):
  - Opacity: 0.5
  - Cursor: not-allowed

---

### 4. Preview Panel (Right)
**Position:** Fixed right side
**Width:** 40% of viewport (min 400px, max 600px)
**Padding:** 32px
**Display:** flex column

#### 4a. Preview Container
**Aspect Ratio:** 1:1 (square)
**Width:** 100%
**Background:** #16213e
**Border:** 2px solid #2a3f5f
**Border Radius:** 16px
**Padding:** 32px
**Display:** flex
**Align:** center
**Justify:** center
**Margin Bottom:** 16px

**Preview Content:**

**Empty/Default State:**
```
┌─────────────────────┐
│                     │
│                     │
│        ✧            │
│                     │
│   Your logo will    │
│   appear here       │
│                     │
│                     │
└─────────────────────┘
```
- Icon: Large sparkle/image placeholder (64px, #6b7280)
- Text: "Your logo will appear here" (16px, #6b7280, centered)

**With Generated Logo:**
```
┌─────────────────────┐
│                     │
│   ┌───────────┐     │
│   │           │     │
│   │  [LOGO]   │     │ ← Logo centered, max 512px
│   │   IMAGE   │     │
│   │           │     │
│   └───────────┘     │
│                     │
└─────────────────────┘
```
- Logo image: max-width/height 512px
- Object-fit: contain
- Drop shadow: 0 20px 40px rgba(0, 0, 0, 0.3)
- Animation on load: fade-in + scale from 0.95 to 1 (500ms)

#### 4b. Zoom Controls
**Position:** Bottom right of preview container (absolute)
**Display:** flex gap 8px

**Button (3 buttons: +, -, ⟲):**
- Size: 40px × 40px
- Background: #1e2d4d
- Border: 1px solid #2a3f5f
- Border radius: 8px
- Color: #ffffff
- Cursor: pointer
- Transition: all 150ms

**States:**
- Hover: Background #6c5ce7, border #6c5ce7
- Active: transform scale(0.95)
- Disabled: opacity 0.5, cursor not-allowed

**Buttons:**
1. Zoom In (+): Increases zoom by 25%
2. Zoom Out (-): Decreases zoom by 25%
3. Reset (⟲): Returns to 100% zoom

#### 4c. Download Button
**Width:** 100%
**Height:** 48px
**Background:** transparent
**Border:** 2px solid #6c5ce7
**Border Radius:** 8px
**Color:** #6c5ce7
**Cursor:** pointer
**Transition:** all 150ms

**Button Content:**
```
┌─────────────────────┐
│ ⬇ Download PNG      │
│   (1024×1024)       │
└─────────────────────┘
```
- Icon: Download (left, 20px)
- Text: "Download PNG" (16px Inter Bold)
- Sub-text: "(1024×1024)" (14px, below)
- Justify: center, align: center

**States:**
- Default: Border #6c5ce7, color #6c5ce7
- Hover: Background #6c5ce7, color #ffffff
- Active: transform scale(0.98)
- Disabled (no logo):
  - Opacity: 0.5
  - Cursor: not-allowed
  - Border: #2a3f5f
  - Color: #6b7280

---

## Color Swatches

```
Main Background:  ███ #1a1a2e
Surface:         ███ #16213e
Surface Elevated: ███ #1e2d4d
Primary Purple:   ███ #6c5ce7
Border:          ███ #2a3f5f
Text Primary:    ███ #ffffff
Text Secondary:  ███ #a0a0a0
Text Tertiary:   ███ #6b7280
```

---

## Interaction Flow

1. **Page Load**
   - Empty state shown in preview
   - History panel shows empty or previous sessions (from localStorage)
   - Prompt input has focus
   - Generate button is disabled

2. **User Types Prompt**
   - Input border becomes purple on focus
   - Character count updates (if shown)
   - Generate button remains disabled until style selected

3. **User Selects Style**
   - Clicked style card gets selected state (purple border, elevated)
   - Previous selection deselected
   - Generate button becomes enabled

4. **User Clicks Generate**
   - Button shows loading state (spinning icon, "Generating...")
   - Loading overlay appears over preview panel
   - API call initiated

5. **Logo Generates**
   - Preview updates with fade-in animation
   - Loading state removed
   - Download button enables
   - New item added to top of history list
   - History scrolls to top smoothly

6. **User Interacts with Logo**
   - Can zoom in/out with controls
   - Can pan if zoomed
   - Can download via download button
   - Can select different history item to load

---

## Responsive Behavior

At **1280px and below:**
- Preview panel reduces to 50% width
- Main content area adjusts accordingly
- Style cards remain same size

At **1024px and below:**
- History panel collapses to drawer (hamburger icon)
- Preview moves below main content
- Single column layout
- Preview width: 100% of container

At **768px and below (Mobile):**
- Header height: 64px
- Title font size: 24px
- All padding reduces to 16px
- Prompt input min-height: 100px
- Style cards: horizontal scroll with snap
- Preview: full width, maintains 1:1 aspect
- Download button: sticky at bottom
- History: bottom drawer, swipe up to open

---

## Assets Needed

### Icons (SVG, 24px unless noted)
- ✨ Sparkle/Star (20px for button)
- ⬇ Download (20px)
- + Plus/Zoom In (16px)
- - Minus/Zoom Out (16px)
- ⟲ Reset/Refresh (16px)
- ☰ Menu/Hamburger (for mobile drawer)
- ✧ Placeholder sparkle (64px, decorative)

### Style Icons (80px × 80px, SVG)
- Minimal icon
- Bold icon
- Playful icon
- Professional icon
- Vintage icon
- Modern icon

### Fonts
- Inter (400, 700) - via Google Fonts
- JetBrains Mono (400) - via Google Fonts

---

## Implementation Priority

**Phase 1 - Core Structure:**
1. Layout grid (3 columns: history, main, preview)
2. Header component
3. Basic styling with colors

**Phase 2 - Input & Selection:**
4. Prompt textarea component
5. Style selector with selection state
6. Generate button with states

**Phase 3 - Preview & Download:**
7. Preview panel with placeholder
8. Image display with animation
9. Download button functionality

**Phase 4 - History:**
10. History panel UI
11. LocalStorage integration
12. Click to load functionality

**Phase 5 - Enhancements:**
13. Zoom/pan controls
14. Loading states
15. Error handling UI

**Phase 6 - Responsive:**
16. Tablet breakpoint adjustments
17. Mobile layout with drawers
18. Touch interactions

---

**Designer:** Pixel 🎨
**File:** MAIN_INTERFACE_MOCKUP.md
**Date:** 2026-01-30
**For Implementation By:** Bolt ⚡
