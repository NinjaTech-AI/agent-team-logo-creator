# UI States: Loading & Error Designs

**Component:** Loading & Error States
**Date:** 2026-01-30
**Designer:** Pixel 🎨

---

## Overview

This document defines all loading and error states for the Logo Creator application, ensuring users always understand what's happening and can recover from errors gracefully.

---

## 1. Loading States

### 1.1 Generation Loading (Primary)

**Context:** User has clicked "Generate Logo" and API request is in progress

**Visual Design:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                                                         │
│                      ◐ ◓ ◑ ◒                           │
│                   (spinning dots)                      │
│                                                         │
│               Generating your logo...                  │
│                                                         │
│            This may take a few seconds                 │
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

**Full-screen Overlay:**
```css
.loading-overlay {
  /* Position */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;

  /* Styling */
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(4px);

  /* Layout */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;

  /* Animation */
  animation: fadeIn 150ms ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**Spinner:**
```css
.loading-spinner {
  width: 60px;
  height: 60px;
  position: relative;
}

.spinner-dot {
  width: 12px;
  height: 12px;
  background: #6c5ce7;
  border-radius: 50%;
  position: absolute;
  animation: spinnerRotate 1.2s linear infinite;
}

.spinner-dot:nth-child(1) {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 0s;
}

.spinner-dot:nth-child(2) {
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  animation-delay: 0.3s;
}

.spinner-dot:nth-child(3) {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 0.6s;
}

.spinner-dot:nth-child(4) {
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  animation-delay: 0.9s;
}

@keyframes spinnerRotate {
  0%, 20% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(0.6);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
```

**Text:**
```css
.loading-text {
  /* Typography */
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 18px;
  line-height: 28px;
  color: #ffffff;
  text-align: center;
}

.loading-subtext {
  /* Typography */
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 20px;
  color: #a0a0a0;
  text-align: center;
}
```

**HTML Structure:**
```html
<div class="loading-overlay" role="alert" aria-live="polite" aria-busy="true">
  <div class="loading-spinner" aria-hidden="true">
    <div class="spinner-dot"></div>
    <div class="spinner-dot"></div>
    <div class="spinner-dot"></div>
    <div class="spinner-dot"></div>
  </div>
  <p class="loading-text">Generating your logo...</p>
  <p class="loading-subtext">This may take a few seconds</p>
</div>
```

---

### 1.2 Button Loading State

**Context:** Generate button is loading

**Visual:**
```
┌──────────────────────┐
│  ◐  Generating...    │  ← Icon spins, text changes
└──────────────────────┘
```

**Implementation:**
```css
.generate-button.loading {
  cursor: not-allowed;
  pointer-events: none;
}

.generate-button.loading .button-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.generate-button.loading .button-text {
  /* Text changes via JS: "Generate Logo" → "Generating..." */
}
```

**React Implementation:**
```jsx
<button
  className={`generate-button ${isLoading ? 'loading' : ''}`}
  disabled={isLoading || !canGenerate()}
  onClick={handleGenerate}
>
  <SparkleIcon className={`button-icon ${isLoading ? 'spinning' : ''}`} />
  <span className="button-text">
    {isLoading ? 'Generating...' : 'Generate Logo'}
  </span>
</button>
```

---

### 1.3 History Panel Loading

**Context:** Loading previous session from localStorage

**Visual:**
```
┌──────────────┐
│ Recent Gens  │
│              │
│   ◐ ◓ ◑ ◒    │ ← Small spinner
│              │
│  Loading...  │
│              │
└──────────────┘
```

**Implementation:**
```css
.history-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
}

.history-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #2a3f5f;
  border-top-color: #6c5ce7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
```

---

### 1.4 Image Loading (Skeleton)

**Context:** Logo image is being fetched/loaded

**Visual:**
```
┌─────────────────────┐
│                     │
│   ┌───────────┐     │
│   │░░░░░░░░░░░│     │ ← Shimmer effect
│   │░░░░░░░░░░░│     │
│   │░░░░░░░░░░░│     │
│   │░░░░░░░░░░░│     │
│   └───────────┘     │
│                     │
└─────────────────────┘
```

**Implementation:**
```css
.image-skeleton {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    #16213e 0%,
    #1e2d4d 50%,
    #16213e 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 2. Error States

### 2.1 Generation Error (Primary)

**Context:** API request failed during logo generation

**Visual:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                         ⚠️                              │
│                                                         │
│              Failed to generate logo                   │
│                                                         │
│         The AI service is temporarily unavailable.     │
│                  Please try again.                     │
│                                                         │
│              [ Try Again ]  [ Cancel ]                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

**Error Modal:**
```css
.error-modal {
  /* Position */
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1001;

  /* Size */
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;

  /* Styling */
  background: #16213e;
  border: 2px solid #ef4444;
  border-radius: 12px;
  padding: 32px;

  /* Layout */
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;

  /* Animation */
  animation: modalSlideIn 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translate(-50%, -48%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

.error-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(4px);
  z-index: 1000;
}
```

**Error Icon:**
```css
.error-icon {
  width: 64px;
  height: 64px;
  color: #ef4444;
  animation: errorShake 400ms ease-in-out;
}

@keyframes errorShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}
```

**Error Text:**
```css
.error-title {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 20px;
  line-height: 28px;
  color: #ffffff;
  text-align: center;
  margin: 0;
}

.error-message {
  font-family: 'Inter', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 20px;
  color: #a0a0a0;
  text-align: center;
  margin: 0;
}
```

**Action Buttons:**
```css
.error-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.error-button-primary {
  padding: 12px 24px;
  background: #6c5ce7;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 150ms;
}

.error-button-primary:hover {
  background: #5f4dd4;
  transform: translateY(-2px);
}

.error-button-secondary {
  padding: 12px 24px;
  background: transparent;
  color: #a0a0a0;
  border: 2px solid #2a3f5f;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 150ms;
}

.error-button-secondary:hover {
  border-color: #6c5ce7;
  color: #ffffff;
}
```

---

### 2.2 Validation Error (Inline)

**Context:** User submits invalid input (e.g., prompt too short, no style selected)

**Visual:**
```
┌──────────────────────────────────────────────────────────┐
│  Describe your logo...                                   │
│  (e.g., 'A modern tech company logo with a rocket')      │
│                                                          │
└──────────────────────────────────────────────────────────┘
│ ⚠️  Prompt must be at least 10 characters long          │
└──────────────────────────────────────────────────────────┘
     ↑ Error message appears below input
```

**Implementation:**
```css
.validation-error {
  /* Styling */
  background: rgba(239, 68, 68, 0.1);
  border-left: 4px solid #ef4444;
  border-radius: 4px;
  padding: 12px 16px;

  /* Layout */
  display: flex;
  align-items: flex-start;
  gap: 12px;

  /* Animation */
  animation: slideDown 200ms ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.validation-error-icon {
  width: 20px;
  height: 20px;
  color: #ef4444;
  flex-shrink: 0;
}

.validation-error-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  line-height: 20px;
  color: #ef4444;
  margin: 0;
}
```

**Auto-dismiss:**
```javascript
// Show error for 5 seconds, then fade out
setTimeout(() => {
  setError(null);
}, 5000);
```

---

### 2.3 Network Error (Toast)

**Context:** Network connectivity issues

**Visual:**
```
┌─────────────────────────────────────────┐
│ ⚠️  Network error. Check your          │
│     internet connection and try again.  │
└─────────────────────────────────────────┘
  ↑ Toast notification (top-right corner)
```

**Implementation:**
```css
.toast-notification {
  /* Position */
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 2000;

  /* Size */
  max-width: 400px;
  min-width: 300px;

  /* Styling */
  background: #16213e;
  border: 2px solid #ef4444;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);

  /* Layout */
  display: flex;
  align-items: flex-start;
  gap: 12px;

  /* Animation */
  animation: toastSlideIn 300ms cubic-bezier(0.4, 0.0, 0.2, 1);
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast-notification.exit {
  animation: toastSlideOut 300ms cubic-bezier(0.4, 0.0, 1, 1);
}

@keyframes toastSlideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
```

---

### 2.4 Empty State (No Results)

**Context:** User has no generated logos yet

**Visual:**
```
┌──────────────┐
│ Recent Gens  │
│              │
│      ✧       │
│              │
│  No logos    │
│   yet        │
│              │
│ Your gen'd   │
│ logos will   │
│ appear here  │
│              │
└──────────────┘
```

**Implementation:**
```css
.empty-state {
  /* Layout */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 32px 16px;
  text-align: center;
}

.empty-state-icon {
  width: 48px;
  height: 48px;
  color: #6b7280;
  margin-bottom: 16px;
}

.empty-state-title {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 24px;
  color: #a0a0a0;
  margin: 0 0 8px 0;
}

.empty-state-description {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  line-height: 20px;
  color: #6b7280;
  margin: 0;
}
```

---

### 2.5 Input Error States

**Prompt Textarea Error:**
```css
.prompt-input.error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.prompt-input.error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
```

**Error Messages:**
| Condition | Message |
|-----------|---------|
| Empty prompt | "Please enter a description for your logo" |
| Prompt too short | "Prompt must be at least 10 characters long" |
| Prompt too long | "Prompt must be less than 500 characters" |
| No style selected | "Please select a style before generating" |
| Network error | "Network error. Check your internet connection and try again." |
| API error | "Failed to generate logo. The AI service is temporarily unavailable." |
| Rate limit | "Too many requests. Please wait a moment and try again." |
| Unknown error | "Something went wrong. Please try again." |

---

## 3. Success States

### 3.1 Generation Success

**Context:** Logo successfully generated

**Visual:**
```
Logo fades in with scale animation
↓
Toast appears briefly
┌──────────────────────────────┐
│ ✓  Logo generated!           │
└──────────────────────────────┘
```

**Implementation:**
```css
.logo-image {
  animation: logoAppear 500ms cubic-bezier(0.4, 0.0, 0.2, 1);
}

@keyframes logoAppear {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.success-toast {
  background: #16213e;
  border: 2px solid #10b981;
  /* ... similar to error toast ... */
}
```

---

### 3.2 Download Success

**Context:** Logo successfully downloaded

**Visual:**
```
Download button briefly shows success state
┌─────────────────┐
│ ✓ Downloaded!   │ ← Changes for 2 seconds
└─────────────────┘
```

**Implementation:**
```javascript
const handleDownload = async () => {
  try {
    await downloadLogo();
    setDownloadState('success');
    setTimeout(() => setDownloadState('default'), 2000);
  } catch (error) {
    setDownloadState('error');
  }
};
```

---

## 4. Accessibility

### Screen Reader Announcements

**Loading:**
```html
<div role="status" aria-live="polite" aria-atomic="true">
  Generating logo, please wait...
</div>
```

**Error:**
```html
<div role="alert" aria-live="assertive" aria-atomic="true">
  Error: Failed to generate logo. Please try again.
</div>
```

**Success:**
```html
<div role="status" aria-live="polite" aria-atomic="true">
  Logo generated successfully. Download button is now available.
</div>
```

### Focus Management

**On Error:**
- Focus moves to error message
- User can tab to "Try Again" button
- Escape key dismisses modal

**On Success:**
- Focus remains on page
- Announcement made via screen reader
- User can continue interaction naturally

---

## 5. Component API

### React Component Props

```typescript
interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
  subMessage?: string;
}

interface ErrorModalProps {
  isVisible: boolean;
  title: string;
  message: string;
  primaryAction: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  onClose: () => void;
}

interface ValidationErrorProps {
  message: string;
  isVisible: boolean;
  autoDismiss?: boolean;
  dismissAfter?: number; // milliseconds
}

interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number; // milliseconds
  onClose?: () => void;
}
```

---

## 6. Testing Scenarios

### Loading States
- [ ] Loading overlay shows on generate click
- [ ] Button shows loading state
- [ ] Multiple rapid clicks don't cause issues
- [ ] Loading dismisses on success
- [ ] Loading dismisses on error

### Error States
- [ ] Network errors show appropriate message
- [ ] API errors show appropriate message
- [ ] Validation errors appear inline
- [ ] Errors are keyboard accessible
- [ ] Errors can be dismissed
- [ ] Screen readers announce errors

### Success States
- [ ] Success animation plays smoothly
- [ ] Success toast appears and auto-dismisses
- [ ] Download shows success state temporarily
- [ ] Multiple successes don't overlap

---

## 7. Implementation Priority

**Phase 1:**
1. Loading overlay for generation
2. Button loading state
3. Basic error modal

**Phase 2:**
4. Validation errors (inline)
5. Empty states
6. Skeleton loaders

**Phase 3:**
7. Success animations
8. Toast notifications
9. Advanced error recovery

---

**Designer:** Pixel 🎨
**Document:** Loading & Error States
**Date:** 2026-01-30
**Status:** Ready for Implementation
