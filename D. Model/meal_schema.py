"""
Meal Schema dan Output Contract
Definisikan struktur output final untuk algoritma meal planning

Output final akan selalu mengikuti kontrak ini, terlepas dari algoritma Greedy atau Genetic.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class FoodItem:
    """Representasi satu item makanan dalam menu"""
    fdc_id: str
    food_name: str
    food_group: str
    consumption_label: str  # Main, Side Dish, Drink, Snack
    cuisine_label: str
    portion_gram: float  # Portion size dalam gram (bukan per 100g)
    energy_kcal: float
    protein_g: float
    carbohydrate_g: float
    fat_g: float
    # Tambahan nutrient lainnya bisa di-extend di sini
    
    def to_dict(self):
        """Convert ke dictionary untuk serialization"""
        return asdict(self)


@dataclass
class MealCourse:
    """Representasi satu course dalam meal (Main/Side/Drink)"""
    course_type: str  # 'Main', 'Side', 'Drink'
    candidates: List[FoodItem]  # Max 3 candidates
    total_calories: float
    total_protein_g: float
    total_carb_g: float
    total_fat_g: float
    
    def to_dict(self):
        return {
            'course': self.course_type,
            'candidates': [item.to_dict() for item in self.candidates],
            'totals': {
                'calories': round(self.total_calories, 2),
                'protein_g': round(self.total_protein_g, 2),
                'carb_g': round(self.total_carb_g, 2),
                'fat_g': round(self.total_fat_g, 2)
            }
        }


@dataclass
class Meal:
    """Representasi satu waktu makan (Breakfast/Lunch/Dinner)"""
    meal_type: str  # 'Breakfast', 'Lunch', 'Dinner'
    courses: Dict[str, MealCourse]  # {'Main': MealCourse, 'Side': MealCourse, 'Drink': MealCourse (optional)}
    target_calories: float
    actual_calories: float
    include_drink: bool
    
    def to_dict(self):
        return {
            'meal': self.meal_type,
            'target_calories': self.target_calories,
            'actual_calories': round(self.actual_calories, 2),
            'include_drink': self.include_drink,
            'courses': {name: course.to_dict() for name, course in self.courses.items()}
        }


@dataclass
class SnackMeal:
    """Representasi snack (tidak ada sub-course, cukup 3 kandidat)"""
    meal_type: str = 'Snack'
    candidates: List[FoodItem] = field(default_factory=list)  # Max 3 candidates
    target_calories: float = 0
    actual_calories: float = 0
    
    def to_dict(self):
        return {
            'meal': self.meal_type,
            'target_calories': self.target_calories,
            'actual_calories': round(self.actual_calories, 2),
            'candidates': [item.to_dict() for item in self.candidates]
        }


@dataclass(init=False)
class MenuPlan:
    """Kontrak output final - struktur 9 slots + 1 snack"""
    algorithm_used: str  # 'Greedy' atau 'Genetic'
    user_profile: Dict  # Dari NutritionService
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    snack: Optional[SnackMeal]
    total_daily_calories: float
    total_daily_protein_g: float
    total_daily_carb_g: float
    total_daily_fat_g: float
    feasible: bool  # Semua constraints terpenuhi
    violations: List[str]  # List constraint violations

    def __init__(
        self,
        algorithm_used: str,
        user_profile: Dict,
        breakfast: Meal,
        lunch: Meal,
        dinner: Meal,
        snack: Optional[SnackMeal],
        total_daily_calories: float = 0,
        total_daily_protein_g: float = 0,
        total_daily_carb_g: float = 0,
        total_daily_fat_g: float = 0,
        feasible: bool = True,
        violations: Optional[List[str]] = None,
        total_calories: Optional[float] = None,
        **_kwargs,
    ):
        self.algorithm_used = algorithm_used
        self.user_profile = user_profile
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner
        self.snack = snack
        self.total_daily_calories = total_daily_calories or (total_calories or 0)
        self.total_daily_protein_g = total_daily_protein_g
        self.total_daily_carb_g = total_daily_carb_g
        self.total_daily_fat_g = total_daily_fat_g
        self.feasible = feasible
        self.violations = violations or []

    @property
    def total_calories(self):
        return self.total_daily_calories
    
    def to_dict(self):
        """Convert ke dictionary untuk JSON response"""
        return {
            'algorithm': self.algorithm_used,
            'user_profile': self.user_profile,
            'meals': {
                'breakfast': self.breakfast.to_dict(),
                'lunch': self.lunch.to_dict(),
                'dinner': self.dinner.to_dict(),
                'snack': self.snack.to_dict() if self.snack else None
            },
            'daily_totals': {
                'calories': round(self.total_daily_calories, 2),
                'protein_g': round(self.total_daily_protein_g, 2),
                'carb_g': round(self.total_daily_carb_g, 2),
                'fat_g': round(self.total_daily_fat_g, 2)
            },
            'feasible': self.feasible,
            'violations': self.violations
        }


class MealDistribution:
    """
    Skema distribusi kalori per meal course
    
    Skema 1: Dengan drink (MC 60%, SD 25%, Drink 15%)
    Skema 2: Tanpa drink (MC 70%, SD 30%)
    """
    
    SCHEMES = {
        'with_drink': {
            'Main': 0.60,
            'Side': 0.25,
            'Drink': 0.15
        },
        'without_drink': {
            'Main': 0.70,
            'Side': 0.30
        }
    }
    
    @staticmethod
    def distribute(meal_calories: float, include_drink: bool = True) -> Dict[str, float]:
        """
        Bagi kalori meal ke courses
        
        Args:
            meal_calories: Total calories untuk meal (breakfast/lunch/dinner)
            include_drink: Apakah user mau include drink atau tidak
        
        Returns:
            Dict dengan course_name: calories
        """
        scheme = MealDistribution.SCHEMES['with_drink'] if include_drink else MealDistribution.SCHEMES['without_drink']
        
        distribution = {}
        for course, percentage in scheme.items():
            distribution[course] = round(meal_calories * percentage, 2)
        
        return distribution


# Example usage untuk dokumentasi
if __name__ == "__main__":
    # Contoh pembuatan struktur
    sample_item = FoodItem(
        fdc_id="167516",
        food_name="Waffles, buttermilk",
        food_group="Baked Products",
        consumption_label="Main",
        cuisine_label="Western",
        portion_gram=100.0,
        energy_kcal=273.0,
        protein_g=6.58,
        carbohydrate_g=41.05,
        fat_g=9.22
    )
    
    # Test distribution
    breakfast_calories = 594  # 23.75% dari 2500
    distribution = MealDistribution.distribute(breakfast_calories, include_drink=True)
    print(f"Distribution dengan drink: {distribution}")
    
    distribution_no_drink = MealDistribution.distribute(breakfast_calories, include_drink=False)
    print(f"Distribution without drink: {distribution_no_drink}")
