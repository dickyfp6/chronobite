# 🎨 NutriPlan Landing Page

## Overview
Landing page yang modern, responsive, dan bilingual (EN/ID) dengan carousel untuk edukasi tentang 5 penyakit kronis sesuai WHO.

## Features

### 1. **Navigation Bar**
- Logo NutriPlan (🥗)
- Language toggle button (English/Bahasa Indonesia)
- Sticky positioning untuk akses mudah

### 2. **Hero Section**
- Animated emoji (🌟 floating effect)
- Main headline & subtitle
- Gradient background (Blue-Green professional theme)
- Responsive typography

### 3. **Disease Carousel/Slider** ⭐
Fitur utama dengan 5 penyakit yang bisa di-slide:
- **Diabetes Type 2** (🩺)
- **Hypertension** (❤️)
- **Cardiovascular Disease** (💓)
- **High Cholesterol** (⚕️)
- **Chronic Kidney Disease** (🫘)

Setiap slide mencakup:
- Deskripsi penyakit yang detail
- Statistik WHO (2 stat per penyakit)
- Smooth transitions
- Navigation buttons (< >)
- Progress indicators (dots)

### 4. **Features Section**
6 kartu yang menjelaskan keunggulan NutriPlan:
- AI-Powered Recommendations
- Disease-Specific Nutrition
- Diverse Food Options
- Health Tracking
- Global Standards
- Privacy Protected

### 5. **Call-to-Action Section**
- Gradient background (sesuai nav)
- Two buttons:
  - **"Get Started"** → Ke /app (main application)
  - **"Learn More"** → Smooth scroll ke disease section

### 6. **Footer**
- Simple copyright text
- Support untuk multilingual

## Multilingual Support (EN/ID)

Semua teks di-hardcode dalam JavaScript object `translations`:
```javascript
const translations = {
  en: { ... },
  id: { ... }
}
```

**Switch bahasa**: Click language toggle button → Semua text dipdate via `updateLanguage()`

## Design Specifications

### Colors
- **Primary**: #0EA5E9 (Sky Blue)
- **Secondary**: #10B981 (Emerald Green)
- **Light BG**: #F0F9FF
- **Text Dark**: #1F2937

### Responsive Breakpoints
- Desktop: Full width carousel dengan image + content side-by-side
- Tablet/Mobile: Carousel stacked (image top, content bottom)

### Typography
- **Font**: Segoe UI, Tahoma, Geneva
- **Hero Title**: 3.5rem (desktop) → 2rem (mobile)
- **Section Headers**: 2.5rem → 1.8rem

## File Structure
```
F. WebApp/
├── templates/
│   ├── landing.html (NEW)
│   └── index.html
├── app.py (UPDATED)
│   ├── @app.route("/") → landing.html
│   └── @app.route("/app") → index.html
```

## Routes
- **`/`** → Landing page (homepage)
- **`/app`** → Main application (previous index)
- **`/api/analyze`** → Existing nutrition analysis endpoint

## Browser Compatibility
✅ Chrome/Edge (latest)
✅ Firefox (latest)
✅ Safari (latest)
✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements
1. Add WHO data dari CSV untuk live statistics
2. Integrase video tentang setiap penyakit
3. Animation pada loading carousel
4. Newsletter signup di footer
5. SEO optimization untuk international reach
