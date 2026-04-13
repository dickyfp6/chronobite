"""
Entry point for Backend API
Usage: python run.py
"""

import os
import sys

# Ensure Backend/ is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True") == "True"
    
    print(f"🚀 Starting Nutrition DSS Backend on port {port}")
    print(f"📡 API endpoints available at http://localhost:{port}/api/")
    print(f"🏥 Health check: GET http://localhost:{port}/health")
    
    app.run(debug=debug, port=port)
