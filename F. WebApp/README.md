# Nutrition DSS - WebApp

Clean full-stack architecture with Python backend (Flask API) and React frontend.

## 🏗️ Project Structure

```
F. WebApp/
├── Backend/
│   ├── app.py                    # Flask app factory
│   ├── run.py                    # Entry point (python run.py)
│   ├── config.py                 # Configuration
│   ├── requirements.txt           # Python dependencies
│   ├── routes/
│   │   ├── analyze.py            # POST /api/analyze
│   │   └── menu.py               # POST /api/generate-menu
│   └── services/
│       └── system_bridge.py      # Adapter to C. System Flow & D. Model
│
├── Frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/           # React components
│   │   ├── services/api.ts       # Backend API calls
│   │   ├── hooks/                # Custom React hooks
│   │   └── ...
│   ├── package.json
│   ├── vite.config.ts
│   └── ...
│
└── README.md (this file)
```

## 🚀 Local Development

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Start Backend

```bash
cd Backend
pip install -r requirements.txt
python run.py
```

Backend runs on: **http://localhost:5000**

Available endpoints:
- `POST /api/analyze` - Profile analysis
- `POST /api/generate-menu` - Menu generation
- `GET /health` - Health check

### Start Frontend (new terminal)

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173**

### Testing the Integration

```bash
# Terminal 1
cd Backend && python run.py

# Terminal 2
cd Frontend && npm run dev

# Browser
open http://localhost:5173
```

## 🔌 API Endpoints

### POST /api/analyze

**Request:**
```json
{
  "gender": "M",
  "age": 30,
  "weight": 70,
  "height": 170,
  "activity": "1.845",
  "diseases": ["normal"],
  "food_preferences": [],
  "algorithm": "greedy"
}
```

**Response:**
```json
{
  "success": true,
  "anthropometrics": {
    "bmi": 24.2,
    "bbi": 63.0,
    "age_group": "young_people"
  },
  "energy": {
    "bmr": 1700,
    "tdee": 2100
  },
  "guidelines": { ... }
}
```

### POST /api/generate-menu

**Request:**
```json
{
  "algorithm": "greedy",
  "user_profile": { ... },
  "analysis_data": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "menu_plan": {
    "meals": { ... },
    "total_calories": 2100,
    "total_protein": 150,
    "total_carbs": 250,
    "total_fat": 70
  }
}
```

## 🧩 Architecture

### Backend Design
- **Thin routes** → call services → call system logic
- **No HTML rendering** → API only
- **system_bridge.py** wraps existing C. System Flow & D. Model logic

### Frontend Design
- **React + Vite + TypeScript**
- **Pages**: Form input, Results display, Menu display
- **Services**: API communication via fetch

### Data Flow

```
React UI
  ↓ (fetch POST /api/analyze)
Backend Route
  ↓ (calls)
Backend Service (system_bridge)
  ↓ (imports)
C. System Flow (NutritionService) ← UNTOUCHED
  ↓
Response back to Frontend
  ↓
Display Results
```

## 🔐 Safety Guarantees

✅ **Core system logic UNTOUCHED**
- `C. System Flow/` - Zero modifications
- `D. Model/` - Zero modifications

✅ **Web layer ISOLATED**
- Backend only calls system via bridges
- Frontend only communicates via REST API

✅ **No rewriting**
- Backend serves as thin adapter layer
- All calculations from original files

## 📦 Dependencies

### Backend
- Flask >= 2.3.0
- Flask-CORS >= 4.0.0
- pandas >= 1.5.0

### Frontend
- React 19.2.4
- Vite 8.0.8
- TypeScript 6.0.2
- Tailwind CSS 4.2.2

## 🔧 Build for Production

### Backend
```bash
cd Backend
# Ready for deployment to Render, Heroku, etc.
# Just run: python run.py
```

### Frontend
```bash
cd Frontend
npm run build
# Creates dist/ folder ready for Vercel, Netlify, etc.
```

## 📝 Notes

- Backend port: 5000 (configurable via PORT env var)
- Frontend port: 5173 (default Vite port)
- CORS allows localhost:5173 and localhost:3000
- Both run independently - can be deployed separately

## 🐛 Troubleshooting

**Backend won't start**
- Ensure C. System Flow and D. Model are in correct paths
- Check: `python -c "import sys; print(sys.path)"`

**Frontend API calls fail**
- Ensure Backend is running on 5000
- Check browser Dev Tools Network tab
- Verify CORS headers

**Module not found errors**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

---

**Created:** April 13, 2026  
**Architecture:** Clean Full-Stack (Python API + React Frontend)  
**Status:** Ready for Local Development
