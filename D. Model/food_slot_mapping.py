"""
Mapping slot makanan untuk kontrak output final.

File ini menyediakan helper non-algoritmik untuk:
- menandai slot makanan berdasarkan label dataset
- memisahkan kandidat per meal slot
- menampung fitur refresh / exclude list

Algoritma manual Greedy dan Genetic nanti boleh memakai helper ini,
tapi file ini sendiri tidak mengandung optimasi.
"""

from typing import Dict, List, Optional


MAIN_COURSE_HINTS = {
    "rice", "nasi", "beef", "ayam", "chicken", "fish", "ikan", "salmon",
    "tuna", "egg", "telur", "tofu", "tempe", "mushroom", "mie", "noodle",
    "pasta", "bread", "roti", "meat"
}

SIDE_DISH_HINTS = {
    "vegetable", "sayur", "salad", "soup", "sup", "potato", "kentang",
    "fries", "chips", "side", "lauk", "tempe", "tofu", "fruit", "buah"
}

DRINK_HINTS = {
    "water", "juice", "tea", "milk", "coffee", "soda", "drink", "minuman",
    "smoothie", "shake", "yogurt", "buttermilk"
}

SNACK_HINTS = {
    "snack", "dessert", "sweets", "cake", "cookie", "biscuit", "bar", "chips",
    "cracker", "popcorn", "pudding", "ice cream", "waffle"
}


def _normalize_text(value: Optional[str]) -> str:
    return str(value or "").strip().lower()


def infer_food_role(food_row: Dict) -> str:
    """
    Infer role makanan: main_course, side_dish, drink, snack, atau unknown.

    Prioritas inferensi:
    1. consumption_label
    2. food_group
    3. food_name
    """

    text_parts = [
        _normalize_text(food_row.get("consumption_label")),
        _normalize_text(food_row.get("food_group")),
        _normalize_text(food_row.get("food_name")),
        _normalize_text(food_row.get("cuisine_label")),
    ]
    merged = " ".join(text_parts)

    if any(hint in merged for hint in DRINK_HINTS):
        return "drink"
    if any(hint in merged for hint in MAIN_COURSE_HINTS):
        return "main_course"
    if any(hint in merged for hint in SIDE_DISH_HINTS):
        return "side_dish"
    if any(hint in merged for hint in SNACK_HINTS):
        return "snack"

    return "unknown"


def group_food_candidates(food_rows: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Kelompokkan daftar makanan ke slot role masing-masing.

    Returns:
        {
            'main_course': [...],
            'side_dish': [...],
            'drink': [...],
            'snack': [...],
            'unknown': [...]
        }
    """

    groups = {
        "main_course": [],
        "side_dish": [],
        "drink": [],
        "snack": [],
        "unknown": [],
    }

    for row in food_rows:
        role = infer_food_role(row)
        groups.setdefault(role, []).append(row)

    return groups


def filter_excluded_items(food_rows: List[Dict], excluded_ids: Optional[List[int]] = None) -> List[Dict]:
    """Filter makanan berdasarkan excluded IDs untuk refresh kandidat."""
    excluded_ids = set(excluded_ids or [])
    if not excluded_ids:
        return list(food_rows)

    filtered = []
    for row in food_rows:
        food_id = row.get("fdc_id")
        if food_id is None:
            filtered.append(row)
            continue

        try:
            if int(food_id) not in excluded_ids:
                filtered.append(row)
        except (TypeError, ValueError):
            filtered.append(row)

    return filtered


def build_refresh_request(meal_name: str, slot_name: Optional[str] = None, excluded_ids: Optional[List[int]] = None) -> Dict[str, object]:
    """Bangun payload refresh untuk UI atau layer algoritma."""
    return {
        "meal_name": meal_name,
        "slot_name": slot_name,
        "excluded_ids": excluded_ids or [],
    }
