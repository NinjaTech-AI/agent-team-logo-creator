# Sample Wireframe - E-Commerce Product Page

**Created by:** Pixel 🎨
**Date:** 2026-01-30
**Purpose:** Sample wireframe demonstration

---

## Layout Structure

```
┌────────────────────────────────────────────────────────────┐
│                        HEADER                               │
│  [Logo]              [Search Bar]         [Cart] [Profile]  │
└────────────────────────────────────────────────────────────┘
│
┌────────────────────────────────────────────────────────────┐
│  MAIN CONTENT AREA                                          │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │                      │  │  Product Title            │   │
│  │   Product Image      │  │                           │   │
│  │     (Large)          │  │  ⭐⭐⭐⭐⭐ (128 reviews)   │   │
│  │                      │  │                           │   │
│  │   [< Prev] [Next >]  │  │  Price: $99.99            │   │
│  │                      │  │                           │   │
│  └──────────────────────┘  │  [Color Selector]         │   │
│                             │  ○ Black  ○ White  ○ Blue │   │
│  ┌──────────────────────┐  │                           │   │
│  │  Thumbnail Gallery   │  │  [Size Selector]          │   │
│  │  [img] [img] [img]   │  │  □ S  □ M  □ L  □ XL      │   │
│  └──────────────────────┘  │                           │   │
│                             │  Quantity: [- 1 +]        │   │
│                             │                           │   │
│                             │  [ Add to Cart ]          │   │
│                             │  [ Buy Now ]              │   │
│                             └──────────────────────────────┘
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PRODUCT DETAILS                                      │  │
│  │  ─────────────────────────────────────────────────   │  │
│  │                                                       │  │
│  │  Description:                                         │  │
│  │  Lorem ipsum dolor sit amet, consectetur adipiscing  │  │
│  │  elit. High-quality materials...                     │  │
│  │                                                       │  │
│  │  Features:                                            │  │
│  │  • Feature 1                                          │  │
│  │  • Feature 2                                          │  │
│  │  • Feature 3                                          │  │
│  │                                                       │  │
│  │  Specifications:                                      │  │
│  │  Material: Cotton blend                               │  │
│  │  Weight: 150g                                         │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CUSTOMER REVIEWS                                     │  │
│  │  ─────────────────────────────────────────────────   │  │
│  │                                                       │  │
│  │  ⭐⭐⭐⭐⭐  "Amazing product!"  - John D.             │  │
│  │  ⭐⭐⭐⭐    "Good quality"      - Sarah M.           │  │
│  │  ⭐⭐⭐⭐⭐  "Fast shipping"     - Mike P.             │  │
│  │                                                       │  │
│  │  [ Load More Reviews ]                                │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  RELATED PRODUCTS                                     │  │
│  │  ─────────────────────────────────────────────────   │  │
│  │                                                       │  │
│  │  [Product 1]  [Product 2]  [Product 3]  [Product 4]  │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└────────────────────────────────────────────────────────────┘
│
┌────────────────────────────────────────────────────────────┐
│                        FOOTER                               │
│  About | Contact | Shipping | Returns | FAQ                │
│  © 2026 Company Name                                        │
└────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### Header
- **Height:** 80px
- **Background:** White (#FFFFFF)
- **Logo:** Left-aligned, 120px width
- **Search Bar:** Center, 400px width, rounded
- **Icons:** Cart and Profile, 24px, right-aligned

### Product Image Section
- **Main Image:** 600x600px
- **Thumbnails:** 80x80px each, 4-6 thumbnails
- **Navigation:** Previous/Next arrows on hover

### Product Details Panel
- **Width:** 400px
- **Price:** Large font (32px), bold
- **Rating:** Star icons + review count
- **Buttons:**
  - Add to Cart: Primary button (blue)
  - Buy Now: Secondary button (outline)

### Reviews Section
- **Layout:** Card-based, 3 reviews visible
- **Rating:** Star display
- **Content:** User name, date, review text (truncated)

### Responsive Behavior
- **Tablet (768px):** Stack image and details vertically
- **Mobile (480px):** Single column layout, full-width buttons

---

## Interaction States

| Element | Default | Hover | Active | Disabled |
|---------|---------|-------|--------|----------|
| **Add to Cart Button** | Blue bg | Darker blue | Pressed effect | Gray bg |
| **Color Selector** | Border gray | Border blue | Filled blue | Opacity 50% |
| **Size Selector** | Border gray | Border blue | Filled blue | Opacity 50% |
| **Image Thumbnails** | Opacity 70% | Opacity 100% | Border blue | N/A |

---

## User Flow

1. **User lands on product page**
2. **Views product images** (main + thumbnails)
3. **Reads product details** (title, price, description)
4. **Selects options** (color, size)
5. **Adjusts quantity** (increment/decrement)
6. **Adds to cart** OR **Buys now**
7. **Reviews other products** (related items)

---

## Design Notes

- **Visual Hierarchy:** Product image is the primary focus
- **White Space:** Generous padding for readability
- **Call-to-Action:** Clear, prominent buttons
- **Trust Signals:** Star ratings, review count visible early
- **Mobile-First:** Responsive design for all screen sizes

---

## Accessibility Considerations

- ✅ High contrast text (WCAG AA compliant)
- ✅ Alt text for all images
- ✅ Keyboard navigation support
- ✅ Screen reader friendly labels
- ✅ Focus indicators on interactive elements

---

🎨 **This is a sample wireframe created by Pixel to demonstrate wireframe structure and documentation style.**
