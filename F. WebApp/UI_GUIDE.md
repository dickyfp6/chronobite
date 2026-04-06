# 📊 NutriPlan DSS - UI/UX Component Guide

## Color Palette Reference

```
Primary Color (Emerald):    #10b981  (rgb(16, 185, 129))
Light Emerald:              #34d399  (rgb(52, 211, 153))
Accent Mint:                #d1fae5  (rgb(209, 250, 229))
Background:                 #f0fdfa  (rgb(240, 253, 250))
Dark Slate:                 #1e293b  (rgb(30, 41, 59))
Light Slate:                #f1f5f9  (rgb(241, 245, 249))
```

## Typography

**Headline Font**: Montserrat
- h1: 7rem (112px) - Hero title
- h2: 2.25rem (36px) - Section titles
- h3: 1.875rem (30px) - Subsection titles
- h4: 1.25rem (20px) - Card titles

**Body Font**: Inter
- Base: 1rem (16px)
- Small: 0.875rem (14px)
- Extra Small: 0.75rem (12px)

## Component Breakdown

### 1. Progress Bar (Top Navigation)
```
┌─────────────────────────────────────────┐
│ Profil Anda                       1 / 5  │
├─────────────────────────────────────────┤
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ (Progress visual)
├─────────────────────────────────────────┤
│ ◯  ◯  ◯  ◯  ◯  (Step indicators)      │
│ Profile Health Analysis Menu            │
└─────────────────────────────────────────┘
```

### 2. Badge Component (Selected State)
```
UNSELECTED:                    SELECTED:
┌──────────────┐              ┌──────────────┐
│ ☑️ Normal    │              │ ✓ Normal     │  (Emerald bg)
└──────────────┘              └──────────────┘
Border: #e2e8f0               Border: #10b981
```

### 3. Input Field
```
┌──────────────────────────────────┐
│ Usia                             │
├──────────────────────────────────┤
│ [Input field with emoji]      🎂 │
└──────────────────────────────────┘
```

### 4. Macro Card (Analysis Slide)
```
┌─────────────────────────────────┐
│ 🍞 Karbohidrat        [emoji] 🌾 │
│                                  │
│ 290g                             │
│ 45-65% dari TDEE                 │
│ ████████████░░░░░░░░  (Progress) │
└─────────────────────────────────┘
Background: Orange-50
Border: Orange-200
```

### 5. Food Card (Menu Slide)
```
┌─────────────────┐
│      🍚         │  (Emoji placeholder)
├─────────────────┤
│ Nasi Tim Ayam   │
│                 │
│ 45g  22g  8g    │  (Carbs, Protein, Fat)
│ Crb  Pro  Fat   │
│                 │
│ 320 cal         │  (Calorie display)
└─────────────────┘
```

### 6. Button States

**Primary Button (CTA)**
```
NORMAL:                   HOVER:
┌──────────────────┐    ┌──────────────────┐
│ Lanjut →         │ →  │ Lanjut →         │ (Slightly raised)
└──────────────────┘    └──────────────────┘
bg: #10b981             bg: #059669 (darker)
```

**Secondary Button**
```
┌──────────────────┐
│ ← Kembali        │
└──────────────────┘
Border: #cbd5e1
Text: #334155
```

## Glassmorphism Effect

```css
.glass-effect {
    background: rgba(255, 255, 255, 0.7);        /* 70% opaque white */
    backdrop-filter: blur(10px);                 /* Blur effect */
    -webkit-backdrop-filter: blur(10px);         /* Safari support */
    border: 1px solid rgba(255, 255, 255, 0.2); /* Subtle border */
}
```

## Animation Timings

- **Fade In**: 0.5s ease-in-out
- **Slide In**: 0.6s ease-out
- **Button Hover**: 0.3s ease
- **Progress Bar**: 0.6s cubic-bezier(0.4, 0, 0.2, 1)

## Responsive Breakpoints

```
Mobile:         < 640px
Tablet:         640px - 1024px
Desktop Large: > 1024px

Grid Adjustments:
- 1 column     (mobile)
- 2 columns    (tablet)
- 3-4 columns  (desktop)
```

## Slide Layout Pattern

```
SLIDE 0: Hero
├── Logo/Title (7rem)
├── Description
├── Illustration
└── CTA Button

SLIDE 1: Profile
├── Title (3rem)
├── Description
├── Form Fields
│   ├── Gender (2-col badge)
│   ├── Age (number)
│   ├── Weight + Height (2-col)
│   ├── Activity Level (select)
│   └── [Emoji indicators]
└── Navigation (Back/Next)

SLIDE 2: Health Condition
├── Title + Description
├── Disease Badges (2-col grid)
├── Food Preference (2-col grid)
└── Navigation

SLIDE 3: Analysis
├── Stats Cards (3-col: BMI, BMR, TDEE)
├── Macro Cards (3-col: Carbs, Protein, Fat)
│   └── Progress bars in each
├── Health Conditions Tag
└── Navigation

SLIDE 4: Menu
├── Meal Type Headers (breakfast, lunch, dinner, snack)
├── 4-col Food Grid
│   └── Food Cards with emoji food images
└── Final Actions (Download/Retry)
```

## Shadow Hierarchy

- **Subtle**: shadow-sm (0 1px 2px)
- **Default**: shadow (0 1px 3px)
- **Hover Impact**: shadow-lg (0 10px 15px)
- **Cards**: shadow-xl

## Interactive States

**Hover**:
- Transform: -4px (slide up)
- Shadow: Increase from shadow to shadow-lg
- Opacity: Slight increase

**Active/Clicked**:
- Transform: Return to original
- Color: Slight darkening
- Duration: Instant

**Focus** (Accessibility):
- Border: 2px solid primary
- Shadow: 0 0 0 3px rgba(primary, 0.1)
- Outline: None

## PWA Indicators

- Status bar color: #10b981
- Splash screen color: #10b981
- App icons: SVG-based (scalable)

## Emoji Usage

| Component | Emoji |
|-----------|-------|
| Profile | 👤 🎂 🏋️ |
| Gender | 👨 👩 |
| Health | 🏥 ❤️ 💔 |
| Foods | 🍚 🥚 🍊 🐟 🥬 |
| Nutrition | 🍞 🥚 🫒 |
| Actions | ➕ ✓ ✗ 📥 |
| Time | 🌅 ☀️ 🌙 🍿 |

## Accessibility Features

✅ **Color Contrast**: WCAG AA (4.5:1 minimum)
✅ **Focus Indicators**: Visible on all interactive elements
✅ **Semantic HTML**: Proper heading hierarchy
✅ **ARIA Labels**: For screen readers
✅ **Keyboard Navigation**: Tab through all elements
✅ **Mobile Touch Targets**: Minimum 44x44px

## Performance Optimizations

- Image: Emoji (SVG data URIs) - no HTTP request
- CSS: Tailwind (utility-first, production: ~15KB gzipped)
- JS: Alpine.js (15KB + dependencies)
- Total Bundle: ~50KB (with CDN optimizations)

---

**Last Updated**: April 2025
