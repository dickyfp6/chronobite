# NutriPlan PWA Setup

Progressive Web App sudah disetup untuk NutriPlan! 🎉

## File yang sudah dibuat:

### 1. **Manifest** (`/public/manifest.json`)
- Konfigurasi PWA
- Nama app, icons, theme color
- Display mode: standalone

### 2. **Service Worker** (`/public/sw.js`)
- Network-first caching strategy
- Offline fallback
- Auto cache cleanup

### 3. **Icons** (`/public/icon-*.png`)
- 192x192px dan 512x512px
- Dengan logo "N" NutriPlan

### 4. **HTML Entry** (`/index.html`)
- Service worker registration
- Manifest link
- iOS meta tags

## Cara Test PWA:

### Desktop (Chrome/Edge):
1. Buka app di browser
2. Klik icon **⊕** atau **ⓘ** di address bar
3. Pilih "Install NutriPlan"
4. App akan muncul seperti aplikasi native

### Mobile (Android):
1. Buka app di Chrome
2. Tap menu (⋮)
3. Pilih "Install app" atau "Add to Home screen"
4. App muncul di app drawer

### Mobile (iOS):
1. Buka app di Safari
2. Tap Share button
3. Pilih "Add to Home Screen"
4. App muncul di home screen

## Fitur PWA yang Aktif:

✅ Installable app  
✅ Standalone mode (fullscreen tanpa browser bar)  
✅ Offline fallback  
✅ Caching untuk performa  
✅ App icon & splash screen  
✅ Desktop & mobile support  

## Development:

Untuk test PWA, app harus dijalankan di:
- **HTTPS** (production)
- **localhost** (development)

Service worker hanya akan register di environment ini untuk keamanan.

## Customize Icons:

Untuk ganti icon dengan design sendiri:
1. Buat icon 512x512px (PNG/SVG)
2. Resize ke 192x192px
3. Replace `/public/icon-192.png` dan `/public/icon-512.png`
4. Clear cache browser & reinstall

## Testing Checklist:

- [ ] Install app dari browser
- [ ] Test offline mode
- [ ] Test app icon tampil
- [ ] Test fullscreen mode
- [ ] Test di mobile device
- [ ] Test uninstall & reinstall

---

**Note:** PWA memerlukan HTTPS untuk production. Di localhost tetap bisa test tanpa HTTPS.
