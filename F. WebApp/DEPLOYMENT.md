# NutriPlan DSS WebApp - Development & Deployment Guide

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
cd "F. WebApp"
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### 2. Run Server
```bash
python app.py
```
Akses: http://localhost:5000

### 3. Testing PWA Locally
- Open DevTools (F12)
- Application Tab → Manifest: Pastikan ada
- Service Workers: Cek status "Activated"
- Offline Tab: Simulate offline dan test functionality

## Production Deployment

### Option 1: Gunicorn + Nginx (Linux/Mac)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Configure Nginx
# /etc/nginx/sites-available/nutriplan
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/F. WebApp/static/;
        expires 30d;
    }
}
```

### Option 2: Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Deploy:
```bash
heroku create nutriplan-dss
git push heroku main
```

### Option 3: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build & Run:
```bash
docker build -t nutriplan-dss .
docker run -p 5000:5000 nutriplan-dss
```

## Environment Variables

Create `.env`:
```
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
DEBUG=False
```

Update `app.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['DEBUG'] = os.getenv('DEBUG', False)
```

## Performance Optimization

### Enable Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/analyze', methods=['POST'])
@cache.cached(timeout=3600, query_string=True)
def analyze():
    ...
```

### Minify Assets
```bash
pip install pillow csscompressor jsmin
```

### CDN for Static Assets
Update `index.html`:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/...">
```

## Monitoring & Logging

Add logging:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('nutriplan.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app.logger.addHandler(file_handler)
```

## SSL/HTTPS Setup

### With Let's Encrypt
```bash
# Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com

# Nginx config update
listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

## Database Integration (Future)

When ready to add database:

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/nutriplan'
db = SQLAlchemy(app)

class UserAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    analysis_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## Performance Benchmarks

Target metrics:
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3.5s

Test dengan:
```bash
# Google PageSpeed Insights
https://pagespeed.web.dev/

# Lighthouse
Chrome DevTools → Lighthouse
```

## Troubleshooting

### CORS Issues
```python
from flask_cors import CORS
CORS(app)
```

### Service Worker caching issues
```javascript
// In sw.js
// Add version to cache name
const CACHE_NAME = 'nutriplan-v' + new Date().getTime();
```

### Form data not submitting
- Check CSRF token (if added)
- Verify API endpoint
- Check browser console for errors

## Git Workflow

```bash
# Feature branch
git checkout -b feature/new-feature

# Commit
git add .
git commit -m "feat: add new feature"

# Push & PR
git push origin feature/new-feature
```

## vs Code Extensions Recommended

- Python
- Pylance
- Flask
- Thunder Client / REST Client
- Tailwind CSS IntelliSense
- Live Server

## Contact & Support

For issues or questions regarding deployment, contact the development team.
