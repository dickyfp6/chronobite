# React Migration Deployment Guide

## ✅ Completed Setup

### React Project Structure Created
- **Location**: `nutrition-dss-react/`
- **Framework**: Vite + React + TypeScript
- **UI**: Tailwind CSS
- **State Management**: React hooks + localStorage

### Components Built
✅ **UserForm.tsx** - Complete user input form with:
  - Gender selector (radio buttons with icons)
  - Age/Weight/Height inputs  
  - Activity factor dropdown
  - Health conditions checkboxes
  - Algorithm selection (Greedy/Genetic)

✅ **ProfileResults.tsx** - Analysis results display:
  - BMI calculation & classification
  - BBR, BMR, TDEE metrics
  - Personal data summary

✅ **MenuDisplay.tsx** - Menu presentation:
  - Meal cards by time (breakfast, lunch, dinner, snack)
  - Macro nutrients summary
  - Item details modal
  - Download & regenerate buttons

✅ **Notifications.tsx** - Toast notification system

✅ **App.tsx** - Main application logic:
  - State management with hooks
  - Tab navigation (Profile, Nutrition, Menu, Constraints)
  - Form submission & menu generation flows
  - LocalStorage persistence

### API Service Layer
✅ **services/api.ts** - Backend communication:
  - `api.analyzeProfile(formData)` → POST `/api/analyze`
  - `api.generateMenu(menuRequest)` → POST `/api/generate-menu`
  - Environment-aware API base URL (dev: localhost:5000, prod: Render URL)

### Hooks Created
✅ **useNotifications.ts** - Notification state & auto-dismiss
✅ **useLocalStorage.ts** - Persistent storage wrapper

### Configuration Files
✅ `.env.development` - Local Flask backend URL
✅ `.env.production` - Production Render backend URL
✅ `tailwind.config.js` - Tailwind configuration
✅ `postcss.config.js` - PostCSS config for Tailwind
✅ `vercel.json` - Vercel deployment settings
✅ `index.css` - Global styles with Tailwind imports

### Backend Updates
✅ **app_integrated.py** - Flask CORS enabled:
  - Allows requests from React dev/prod frontends
  - Configured for localhost:5173 and production domains

✅ **requirements.txt** - Added Flask-CORS dependency

---

## 🚀 Deployment Steps

### 1. Finish Local Setup (npm install)

```bash
cd nutrition-dss-react

# Install Tailwind (still running - wait for completion)
npm install -D tailwindcss postcss autoprefixer

# Start dev server
npm run dev
# Server will be on http://localhost:5173
```

### 2. Test Locally

**In separate terminal, start Flask:**
```bash
cd F. WebApp
python -m venv .venv  # if not already done
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt  # This installs Flask-CORS now
python app_integrated.py
# Should run on http://localhost:5000
```

**Test API endpoints:**
- Navigate to http://localhost:5173 in browser
- Fill out the form
- Click "Analisis Profil" → should call `/api/analyze` on localhost:5000
- Results should appear on Profile tab
- Click Menu tab → click "Buat Menu Sekarang" → should call `/api/generate-menu`
- Menu should render

### 3. Push to GitHub

```bash
cd ..  # Back to TugasAkhirDSS root

git add -A
git commit -m "feat: Migrate WebApp to React + Vite with Tailwind CSS"
git push origin main
```

### 4. Deploy React to Vercel

**Option A: Via Vercel CLI**
```bash
cd nutrition-dss-react
npm install -g vercel
vercel
# Follow prompts:
# - Link existing project? No (new project)
# - Build command: npm run build ✓
# - Output directory: dist ✓
# - It auto-deploys from git repo
```

**Option B: Via Vercel Dashboard**
- Go to vercel.com
- Import GitHub repository
- Select `nutrition-dss-react` as root directory
- Environment Variables:
  - `VITE_API_URL` = `https://nutrition-dss-render.onrender.com` (change this to your Render URL)
- Deploy

**Result**: Your React app at `nutrition-dss-react.vercel.app`

### 5. Deploy Flask to Render

**Create new Web Service on render.com:**

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configuration:
   - **Name**: `nutrition-dss-flask`
   - **Root Directory**: `F. WebApp`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:10000 app_integrated:app`
   - **Environment Variables**:
     - Add any needed by your backend

5. Deploy

**Result**: Your API at `https://nutrition-dss-flask.onrender.com`

### 6. Update Vercel with Render URL

Once Flask is deployed:
1. Go to Vercel project settings
2. Update `VITE_API_URL` environment variable to your Render URL
3. Redeploy Vercel

### 7. Enable CORS if Issues

If frontend shows CORS errors:
- Already configured in app_integrated.py with Flask-CORS
- Make sure to add your Vercel domain to allowed origins:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "https://nutrition-dss-react.vercel.app",  # Add your Vercel URL
            "https://nutrition-dss-render.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

---

## 📋 File Structure Reference

```
nutrition-dss-react/
├── src/
│   ├── components/
│   │   ├── UserForm.tsx
│   │   ├── ProfileResults.tsx
│   │   ├── MenuDisplay.tsx
│   │   └── Notifications.tsx
│   ├── hooks/
│   │   ├── useNotifications.ts
│   │   └── useLocalStorage.ts
│   ├── services/
│   │   └── api.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── .env.development
├── .env.production
├── tailwind.config.js
├── postcss.config.js
├── vercel.json
├── tsconfig.json
├── vite.config.ts
└── package.json

F. WebApp/
├── app_integrated.py (updated with CORS)
├── requirements.txt (updated with Flask-CORS)
└── templates/ (old Alpine templates - can be removed)
```

---

## 🔗 Important URLs After Deployment

| Component | URL |
|-----------|-----|
| Local React | http://localhost:5173 |
| Local Flask | http://localhost:5000 |
| Production React | https://nutrition-dss-react.vercel.app |
| Production API | https://nutrition-dss-flask.onrender.com |

---

## 🐛 Troubleshooting

### "Cannot find module 'react'"
```bash
npm install react react-dom
```

### "Tailwind styles not loading"
```bash
# Make sure these are installed
npm install -D tailwindcss postcss autoprefixer

# Make sure index.css is imported in main.tsx
```

### CORS errors in browser console
- Check Flask CORS configuration in app_integrated.py
- Add your domain to allowed origins
- Redeploy Flask with updated origins

### API calls return 404
- Make sure Flask is running and accessible
- Check the VITE_API_URL environment variable
- Verify backend URL in api.ts is correct

---

## 📝 Next Steps

1. ✅ Wait for `npm install` to finish
2. ✅ Test locally (React on 5173 + Flask on 5000)
3. ✅ Push to GitHub
4. ✅ Deploy React to Vercel
5. ✅ Deploy Flask to Render
6. ✅ Update Vercel environment with Render URL
7. ✅ Test production deployment
8. ✅ Done! Share your URL for presentation

---

**Deployment time estimate**: 15-20 minutes (excluding npm install wait)
