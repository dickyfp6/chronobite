"""
Route: POST /api/analyze
Purpose: Accept user profile, return nutrition analysis
"""

from flask import Blueprint, request, jsonify
from services.system_bridge import analyze_profile

bp = Blueprint("analyze", __name__, url_prefix="/api")


@bp.route("/analyze", methods=["POST"])
def analyze():
    """
    POST /api/analyze
    
    Request body:
    {
        "gender": "M" or "F",
        "age": 30,
        "weight": 70,
        "height": 170,
        "activity": "1.845",
        "diseases": ["normal"],
        "food_preferences": [],
        "algorithm": "greedy"
    }
    
    Response:
    {
        "success": true,
        "anthropometrics": {...},
        "energy": {...},
        "guidelines": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400
        
        # Call system_bridge
        result = analyze_profile(data)

        # The service returns a pandas DataFrame for internal use; remove it before JSON serialization.
        food_data = result.get("food_data")
        if isinstance(food_data, dict):
            food_data = dict(food_data)
            food_data.pop("dataframe", None)
            result["food_data"] = food_data
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__}), 500
