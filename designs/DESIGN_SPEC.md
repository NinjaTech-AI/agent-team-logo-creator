# Logo Creator - Design Specification

> Created by Pixel 🎨 | UX Designer
> Version: 1.0 | Date: 2026-01-29

## Overview

This document contains the complete UI/UX design specifications for the Logo Creator application. All designs follow a modern dark theme aesthetic with purple accent colors.

## Design Files

| File | Description | State |
|------|-------------|-------|
| `logo_creator_main_interface_v1.png` | Main interface - empty state | Default |
| `logo_creator_loading_state_v1.png` | Loading state during generation | Loading |
| `logo_creator_with_logo_v1.png` | Interface with generated logo | Success |
| `logo_creator_history_panel_v1.png` | History panel slide-out | History Open |
| `logo_creator_mobile_view_v1.png` | Mobile responsive layout | Mobile |
| `logo_creator_error_state_v1.png` | Error state after failed generation | Error |

---

## Design System

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Background Primary** | `#1a1a2e` | Header, main background |
| **Background Secondary** | `#2d2d44` | Preview area, cards |
| **Background Tertiary** | `#252538` | Input fields, panels |
| **Accent Primary** | `#6c5ce7` | Buttons, selected states, borders |
| **Accent Gradient** | `#6c5ce7 → #a855f7` | Primary action buttons |
| **Text Primary** | `#ffffff` | Headings, important text |
| **Text Secondary** | `#a0a0b0` | Placeholder text, descriptions |
| **Text Muted** | `#666680` | Disabled states |
| **Error** | `#ef4444` | Error icons, alerts |
| **Success** | `#22c55e` | Success indicators |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| **App Title** | Inter | 24px | Bold |
| **Section Headers** | Inter | 18px | Semibold |
| **Body Text** | Inter | 16px | Regular |
| **Button Text** | Inter | 16px | Semibold |
| **Input Text** | Inter | 16px | Regular |
| **Small Text** | Inter | 14px | Regular |
| **Labels** | Inter | 14px | Medium |

### Spacing

| Size | Value | Usage |
|------|-------|-------|
| **xs** | 4px | Icon padding |
| **sm** | 8px | Tight spacing |
| **md** | 16px | Standard spacing |
| **lg** | 24px | Section spacing |
| **xl** | 32px | Large gaps |
| **2xl** | 48px | Major sections |

### Border Radius

| Element | Radius |
|---------|--------|
| Buttons | 8px |
| Cards | 12px |
| Input fields | 8px |
| Preview area | 12px |
| Thumbnails | 8px |

---

## Component Specifications

### Header Bar

```
Height: 64px
Background: #1a1a2e
Padding: 0 24px
Border-bottom: 1px solid #333355

Logo:
- Icon: 🎨 (24x24)
- Text: "Logo Creator"
- Font: Inter Bold 24px
- Color: #ffffff

History Button:
- Style: Outlined
- Border: 1px solid #666680
- Border-radius: 8px
- Padding: 8px 16px
- Hover: Border color #6c5ce7
```

### Logo Preview Area

```
Desktop:
- Width: 100% (max 900px)
- Height: 400-500px
- Background: #2d2d44
- Border: 1px solid #333355
- Border-radius: 12px
- Margin: 24px auto

Zoom Controls:
- Position: Bottom-right corner
- Buttons: +, -, Reset
- Size: 36x36px each
- Background: #252538
- Border-radius: 6px
- Gap: 8px
```

### Text Input Field

```
Width: 100% (max 900px)
Height: 56px
Background: #252538
Border: 1px solid #333355
Border-radius: 8px
Padding: 16px
Font: Inter Regular 16px
Color: #ffffff
Placeholder color: #666680

Focus state:
- Border: 1px solid #6c5ce7
- Box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2)
```

### Style Selector

```
Layout: Horizontal row (6 items)
Gap: 12px

Style Card:
- Width: 80px
- Height: 80px
- Background: #252538
- Border: 1px solid #333355
- Border-radius: 8px
- Padding: 12px

Icon:
- Size: 32x32px
- Color: #ffffff
- Centered

Label:
- Font: Inter Medium 12px
- Color: #a0a0b0
- Centered below icon

Selected State:
- Border: 2px solid #6c5ce7
- Box-shadow: 0 0 12px rgba(108, 92, 231, 0.4)

Hover State:
- Border: 1px solid #666680
- Background: #2d2d44
```

### Action Buttons

```
Primary Button (Generate):
- Width: 180px
- Height: 48px
- Background: linear-gradient(135deg, #6c5ce7, #a855f7)
- Border: none
- Border-radius: 8px
- Font: Inter Semibold 16px
- Color: #ffffff
- Icon: ✨ (left of text)

Secondary Button (Download):
- Width: 180px
- Height: 48px
- Background: transparent
- Border: 1px solid #6c5ce7
- Border-radius: 8px
- Font: Inter Semibold 16px
- Color: #6c5ce7
- Icon: ⬇️ (left of text)

Disabled State:
- Opacity: 0.5
- Cursor: not-allowed

Loading State:
- Show spinner icon
- Text: "Generating..."
- Disabled interaction
```

### History Panel

```
Position: Fixed, right side
Width: 320px
Height: 100vh
Background: #1e1e32
Border-left: 1px solid #333355
Box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3)

Header:
- Height: 64px
- Padding: 0 20px
- Title: "Recent Generations"
- Close button: X icon

Thumbnail Grid:
- Columns: 2
- Gap: 12px
- Padding: 20px

Thumbnail:
- Size: 130x130px
- Border-radius: 8px
- Border: 2px solid transparent
- Cursor: pointer

Selected Thumbnail:
- Border: 2px solid #6c5ce7
```

---

## States

### Empty State (Default)
- Preview area shows placeholder text: "Your logo will appear here"
- Download button disabled
- Generate button active

### Loading State
- Preview area shows spinner animation
- Text: "Creating your logo..."
- Generate button shows spinner, disabled
- Download button disabled
- Input field and style selector slightly dimmed

### Success State
- Generated logo displayed in preview
- Zoom controls visible
- Download button active with highlight
- Generate button active (for regeneration)

### Error State
- Preview area shows error icon and message
- "Try Again" button in preview area
- Generate button active
- Download button disabled

---

## Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| **Desktop** | ≥1024px | Full horizontal layout |
| **Tablet** | 768-1023px | Slightly compressed, same layout |
| **Mobile** | <768px | Stacked vertical layout |

### Mobile Adaptations
- Header: Hamburger menu, centered title
- Preview: 50% of viewport height
- Style selector: 3x2 grid
- Buttons: Full width, stacked vertically
- History: Full-screen overlay

---

## Animations

### Loading Spinner
- Type: Rotating ring
- Color: Purple gradient (#6c5ce7 → #a855f7)
- Duration: 1.5s per rotation
- Easing: Linear

### Button Hover
- Scale: 1.02
- Duration: 150ms
- Easing: ease-out

### Panel Slide
- Direction: Right to left
- Duration: 300ms
- Easing: ease-in-out

### Thumbnail Hover
- Scale: 1.05
- Border color transition
- Duration: 200ms

---

## Accessibility

### Color Contrast
- All text meets WCAG AA standards (4.5:1 minimum)
- Interactive elements have visible focus states

### Keyboard Navigation
- Tab order: Input → Style cards → Generate → Download → History
- Enter/Space activates buttons
- Escape closes history panel

### Screen Reader
- All images have alt text
- Buttons have aria-labels
- Loading states announced

---

## Handoff Notes for Bolt ⚡

1. **Framework**: Use React 18 + TypeScript + Tailwind CSS
2. **Icons**: Use Lucide React or similar icon library
3. **Animations**: Use Framer Motion for smooth transitions
4. **Zoom/Pan**: Consider react-zoom-pan-pinch library
5. **State Management**: React Query for API calls, useState for UI state

### Key Implementation Points
- Preview area should maintain aspect ratio
- Style selector should be keyboard accessible
- History panel should trap focus when open
- Loading state should prevent multiple submissions
- Error messages should be dismissible

---

*Design by Pixel 🎨 | Ready for implementation*