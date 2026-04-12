"""
Support layer untuk meal planning di folder D. Model.

File ini sengaja hanya mengekspos helper pendukung,
bukan implementasi algoritma optimasi.
"""

from .meal_distribution import (
    MealScheme,
    SCHEME_1,
    SCHEME_2,
    build_meal_budget_plan,
    calculate_meal_budget,
    calculate_slot_budget,
    get_default_meal_ratios,
    get_meal_scheme,
)
from .output_contract import (
    COURSE_SLOT_NAMES,
    MEAL_SLOT_NAMES,
    build_empty_candidate_box,
    build_empty_meal_box,
    build_final_output_template,
    build_refresh_state_template,
    validate_final_output_structure,
)
from .food_slot_mapping import (
    build_refresh_request,
    filter_excluded_items,
    group_food_candidates,
    infer_food_role,
)
from .meal_similarity import (
    diversity_penalty,
    extract_name_tokens,
    get_food_signature,
    is_too_similar,
    similarity_score,
)

__all__ = [
    "MealScheme",
    "SCHEME_1",
    "SCHEME_2",
    "build_meal_budget_plan",
    "calculate_meal_budget",
    "calculate_slot_budget",
    "get_default_meal_ratios",
    "get_meal_scheme",
    "COURSE_SLOT_NAMES",
    "MEAL_SLOT_NAMES",
    "build_empty_candidate_box",
    "build_empty_meal_box",
    "build_final_output_template",
    "build_refresh_state_template",
    "validate_final_output_structure",
    "build_refresh_request",
    "filter_excluded_items",
    "group_food_candidates",
    "infer_food_role",
    "diversity_penalty",
    "extract_name_tokens",
    "get_food_signature",
    "is_too_similar",
    "similarity_score",
]
