"""
Meal distribution schema untuk layer algoritma.

File ini tidak berisi algoritma optimasi.
Fungsinya hanya menyediakan pembagian kalori per meal slot
agar Greedy dan Genetic yang ditulis manual bisa mengikuti kontrak yang sama.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class MealScheme:
    """Konfigurasi pembagian porsi untuk 1 meal."""

    name: str
    has_drink: bool
    main_course_ratio: float
    side_dish_ratio: float
    drink_ratio: float


SCHEME_1 = MealScheme(
    name="scheme_1",
    has_drink=True,
    main_course_ratio=0.60,
    side_dish_ratio=0.25,
    drink_ratio=0.15,
)

SCHEME_2 = MealScheme(
    name="scheme_2",
    has_drink=False,
    main_course_ratio=0.70,
    side_dish_ratio=0.30,
    drink_ratio=0.00,
)

DEFAULT_MEAL_SEQUENCE = ["breakfast", "lunch", "dinner", "snack"]
MEAL_WITH_DRINK = ["breakfast", "lunch", "dinner"]
MEAL_WITHOUT_DRINK = ["snack"]


def get_meal_scheme(meal_name: str, include_drink: bool = True) -> MealScheme:
    """
    Ambil skema pembagian meal berdasarkan nama meal.

    Breakfast/Lunch/Dinner:
    - default pakai skema 1 (MC 60%, SD 25%, Drink 15%)
    - jika drink dimatikan, pakai skema 2 (MC 70%, SD 30%)

    Snack:
    - tidak dipisah jadi MC/SD/Drink
    - tetap direkomendasikan sebagai 3 kandidat item
    """

    meal_name = meal_name.lower().strip()
    if meal_name in MEAL_WITH_DRINK:
        return SCHEME_1 if include_drink else SCHEME_2
    return SCHEME_2


def calculate_meal_budget(tdee: float, meal_ratio: float) -> float:
    """Hitung budget kalori untuk satu meal."""
    return round(tdee * meal_ratio, 2)


def calculate_slot_budget(meal_budget: float, scheme: MealScheme) -> Dict[str, float]:
    """
    Bagi budget meal ke slot Main Course, Side Dish, dan Drink.

    Returns:
        dict dengan keys:
        - main_course
        - side_dish
        - drink
        - total
    """
    main_course = round(meal_budget * scheme.main_course_ratio, 2)
    side_dish = round(meal_budget * scheme.side_dish_ratio, 2)
    drink = round(meal_budget * scheme.drink_ratio, 2)

    return {
        "main_course": main_course,
        "side_dish": side_dish,
        "drink": drink,
        "total": round(main_course + side_dish + drink, 2),
        "scheme_name": scheme.name,
        "has_drink": scheme.has_drink,
    }


def get_default_meal_ratios() -> Dict[str, float]:
    """Return rasio default meal harian yang bisa dipakai algoritma manual."""
    return {
        "breakfast": 0.2375,
        "lunch": 0.3375,
        "dinner": 0.2875,
        "snack": 0.1375,
    }


def build_meal_budget_plan(tdee: float, include_drink: bool = True) -> Dict[str, dict]:
    """
    Bangun rencana budget meal lengkap untuk kontrak output final.

    Struktur hasil:
    {
        'breakfast': {
            'scheme': 'scheme_1',
            'budget': 1234,
            'slots': {'main_course': ..., 'side_dish': ..., 'drink': ...}
        },
        ...
    }
    """

    meal_ratios = get_default_meal_ratios()
    output = {}

    for meal_name, ratio in meal_ratios.items():
        meal_budget = calculate_meal_budget(tdee, ratio)
        scheme = get_meal_scheme(meal_name, include_drink=include_drink)
        slot_budget = calculate_slot_budget(meal_budget, scheme)

        output[meal_name] = {
            "budget": meal_budget,
            "scheme": scheme.name,
            "has_drink": scheme.has_drink,
            "slots": slot_budget,
        }

    return output
