"""
Route: POST /api/generate-menu
Purpose: Generate personalized menu based on analysis
"""

from flask import Blueprint, request, jsonify
from services.system_bridge import generate_menu

bp = Blueprint("menu", __name__, url_prefix="/api")


@bp.route("/generate-menu", methods=["POST"])
def generate_menu_route():
    """
    POST /api/generate-menu
    
    Request body:
    {
        "algorithm": "greedy",
        "user_profile": {...},
        "analysis_data": {...}
    }
    
    Response:
    {
        "success": true,
        "menu_plan": {
            "meals": {...},
            "total_calories": ...,
            "total_protein": ...,
            "total_carbs": ...,
            "total_fat": ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400
        
        # Call system_bridge
        result = generate_menu(data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__}), 500
