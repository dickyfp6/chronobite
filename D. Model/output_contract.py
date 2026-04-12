"""
Kontrak output final untuk algoritma manual Greedy dan Genetic.

File ini hanya mendefinisikan bentuk data yang harus dikembalikan
oleh setiap algoritma agar layer web/CLI bisa menampilkannya secara seragam.
"""

from typing import Dict, List, Any


MEAL_SLOT_NAMES = ["breakfast", "lunch", "dinner", "snack"]
COURSE_SLOT_NAMES = ["main_course", "side_dish", "drink"]


def build_empty_candidate_box() -> Dict[str, List[dict]]:
    """Buat template box kandidat 3 item per slot."""
    return {
        "main_course": [],
        "side_dish": [],
        "drink": [],
    }


def build_empty_meal_box() -> Dict[str, Any]:
    """Buat template output untuk 1 meal."""
    return {
        "budget_kcal": 0,
        "selected": {
            "main_course": None,
            "side_dish": None,
            "drink": None,
        },
        "candidates": build_empty_candidate_box(),
        "refresh_state": {
            "main_course": 0,
            "side_dish": 0,
            "drink": 0,
        },
    }


def build_final_output_template() -> Dict[str, Any]:
    """
    Template output final yang harus dipenuhi algoritma.

    Catatan:
    - Breakfast/Lunch/Dinner memakai main_course, side_dish, drink
    - Snack hanya memakai 3 kandidat tanpa sub-slot wajib
    - Drink bersifat opsional: boleh None atau list kosong
    """
    return {
        "algorithm": None,
        "success": False,
        "user_profile": {},
        "meal_plan": {
            "breakfast": build_empty_meal_box(),
            "lunch": build_empty_meal_box(),
            "dinner": build_empty_meal_box(),
            "snack": {
                "budget_kcal": 0,
                "selected": None,
                "candidates": [],
                "refresh_state": 0,
            },
        },
        "summary": {
            "fitness_score": 0.0,
            "feasible": False,
            "execution_time": 0.0,
            "violations": [],
            "notes": [],
        },
        "debug": {
            "selected_algorithm_mode": None,
            "excluded_food_ids": [],
            "seed": None,
        },
    }


def build_refresh_state_template() -> Dict[str, Any]:
    """Template state untuk fitur refresh kandidat."""
    return {
        "breakfast": {
            "main_course": [],
            "side_dish": [],
            "drink": [],
        },
        "lunch": {
            "main_course": [],
            "side_dish": [],
            "drink": [],
        },
        "dinner": {
            "main_course": [],
            "side_dish": [],
            "drink": [],
        },
        "snack": [],
    }


def validate_final_output_structure(result: Dict[str, Any]) -> List[str]:
    """
    Validasi ringan untuk memastikan hasil algoritma sesuai kontrak.

    Returns:
        list of error messages. Kosong jika valid.
    """
    errors: List[str] = []

    if not isinstance(result, dict):
        return ["Result must be a dictionary"]

    required_top_level = ["algorithm", "success", "meal_plan", "summary"]
    for key in required_top_level:
        if key not in result:
            errors.append(f"Missing top-level key: {key}")

    meal_plan = result.get("meal_plan", {})
    for meal_name in ["breakfast", "lunch", "dinner", "snack"]:
        if meal_name not in meal_plan:
            errors.append(f"Missing meal slot: {meal_name}")

    return errors
