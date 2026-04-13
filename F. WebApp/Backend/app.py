"""
Nutrition DSS - Flask Backend API
Main application factory and CORS setup
"""

from flask import Flask
from flask_cors import CORS
from config import CORS_ORIGINS

# Import route blueprints
from routes import analyze, menu


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # CORS: Allow React frontend to communicate
    CORS(app, resources={
        r"/api/*": {
            "origins": CORS_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(analyze.bp)
    app.register_blueprint(menu.bp)
    
    # Health check route
    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {"error": "Internal server error"}, 500
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
