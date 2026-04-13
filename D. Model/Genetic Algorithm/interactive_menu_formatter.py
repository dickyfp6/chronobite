"""
INTERACTIVE MENU FORMATTER: Display Menu dengan Checklist Options
Mengubah consolidated menu data menjadi interactive checklist output

Features:
- 3 options per meal category (main/side/drink)
- Checklist format dengan radio buttons [ ]
- Snack sebagai separate section
- Nutrition info per option
- Professional formatting
"""

from typing import Dict, List, Optional


class InteractiveMenuFormatter:
    """
    Format consolidated menu options ke interactive checklist
    """
    
    # Styling constants
    CHECKBOX = "[ ]"
    CHECKBOX_SELECTED = "[✓]"
    SEPARATOR = "─" * 80
    TITLE_LINE = "═" * 80
    
    MEALS_ORDER = ['breakfast', 'lunch', 'dinner']
    CATEGORIES_ORDER = ['main_course', 'side_dish', 'drink']
    
    CATEGORY_EMOJI = {
        'main_course': '🍖',
        'side_dish': '🥗',
        'drink': '🥤',
    }
    
    CATEGORY_LABELS = {
        'main_course': 'MAIN COURSE',
        'side_dish': 'SIDE DISH',
        'drink': 'DRINK (Optional)',
    }
    
    MEAL_EMOJI = {
        'breakfast': '🌅',
        'lunch': '🍽️',
        'dinner': '🌙',
        'snack': '🍎',
    }
    
    MEAL_LABELS = {
        'breakfast': 'BREAKFAST',
        'lunch': 'LUNCH',
        'dinner': 'DINNER',
        'snack': 'SNACK',
    }
    
    # ========================================================================
    # MAIN METHODS
    # ========================================================================
    
    @staticmethod
    def display_interactive_menu(
        meal_options: Dict[str, Dict[str, List[Dict]]],
        snack_options: List[Dict],
        user_tdee: Optional[float] = None,
        ga_fitness_score: Optional[float] = None
    ):
        """
        Display complete interactive menu dengan checklist options
        
        Args:
            meal_options: Output dari MenuPostProcessor.process()
                {meal: {category: [top_options], ...}, ...}
            snack_options: Snack list dari MenuPostProcessor.process()
            user_tdee: User's TDEE (optional, for reference)
            ga_fitness_score: GA fitness score (optional)
        """
        
        print("\n" + InteractiveMenuFormatter.TITLE_LINE)
        print("PERSONALIZED MENU - SELECT YOUR OPTIONS")
        print(InteractiveMenuFormatter.TITLE_LINE + "\n")
        
        # Header info
        if ga_fitness_score:
            print(f"Quality Score: {ga_fitness_score:.1f}/100")
        if user_tdee:
            print(f"Daily Target: {user_tdee:.0f} kcal")
        print()
        
        # Display meals
        for meal_name in InteractiveMenuFormatter.MEALS_ORDER:
            
            if meal_name not in meal_options:
                continue
            
            meal_data = meal_options[meal_name]
            
            InteractiveMenuFormatter._display_meal(meal_name, meal_data)
        
        # Display snacks
        if snack_options:
            InteractiveMenuFormatter._display_snacks(snack_options)
        
        # Footer
        print("\n" + InteractiveMenuFormatter.TITLE_LINE)
        print("INSTRUCTIONS:")
        print("  1. Select ONE option from each category using the checkbox [ ]")
        print("  2. DRINK is optional - you can skip if preferred")
        print("  3. Select YOUR favorite options from SNACK if desired")
        print(InteractiveMenuFormatter.TITLE_LINE + "\n")
    
    @staticmethod
    def _display_meal(meal_name: str, meal_data: Dict[str, List[Dict]]):
        """
        Display single meal (breakfast, lunch, dinner)
        """
        
        emoji = InteractiveMenuFormatter.MEAL_EMOJI.get(meal_name, '')
        label = InteractiveMenuFormatter.MEAL_LABELS.get(meal_name, meal_name.upper())
        
        print(f"\n{emoji}  {label}")
        print(InteractiveMenuFormatter.SEPARATOR)
        
        # Display per category
        for category in InteractiveMenuFormatter.CATEGORIES_ORDER:
            
            if category not in meal_data:
                continue
            
            options = meal_data[category]
            
            InteractiveMenuFormatter._display_category(category, options)
        
        print()
    
    @staticmethod
    def _display_category(category: str, options: List[Dict]):
        """
        Display single category dengan 3 pilihan
        """
        
        emoji = InteractiveMenuFormatter.CATEGORY_EMOJI.get(category, '')
        label = InteractiveMenuFormatter.CATEGORY_LABELS.get(category, category.upper())
        
        print(f"\n  {emoji} {label}")
        
        for idx, option in enumerate(options, 1):
            
            food_name = option.get('food_name', 'Unknown')
            portion = option.get('portion', 0)
            energy = option.get('energy_kcal', 0)
            protein = option.get('protein_g', 0)
            carbs = option.get('carbs_g', 0)
            fat = option.get('fat_g', 0)
            
            # Format nutrition info
            nutrition_str = f"({portion:.0f}g | {energy:.0f} kcal | P:{protein:.1f}g C:{carbs:.1f}g F:{fat:.1f}g)"
            
            print(f"    {InteractiveMenuFormatter.CHECKBOX}  [{idx}] {food_name}")
            print(f"            {nutrition_str}")
    
    @staticmethod
    def _display_snacks(snack_options: List[Dict]):
        """
        Display snack section (separate dari meal categories)
        """
        
        if not snack_options:
            return
        
        emoji = InteractiveMenuFormatter.MEAL_EMOJI.get('snack', '')
        label = InteractiveMenuFormatter.MEAL_LABELS.get('snack', 'SNACK')
        
        print(f"\n{emoji}  {label} (OPTIONAL - Select your preference)")
        print(InteractiveMenuFormatter.SEPARATOR)
        print()
        
        for idx, snack in enumerate(snack_options, 1):
            
            food_name = snack.get('food_name', 'Unknown')
            portion = snack.get('portion', 0)
            energy = snack.get('energy_kcal', 0)
            protein = snack.get('protein_g', 0)
            carbs = snack.get('carbs_g', 0)
            fat = snack.get('fat_g', 0)
            
            nutrition_str = f"({portion:.0f}g | {energy:.0f} kcal | P:{protein:.1f}g C:{carbs:.1f}g F:{fat:.1f}g)"
            
            print(f"  {InteractiveMenuFormatter.CHECKBOX}  [{idx}] {food_name}")
            print(f"          {nutrition_str}")
        
        print()
    
    # ========================================================================
    # ALTERNATIVE DISPLAY FORMATS
    # ========================================================================
    
    @staticmethod
    def display_compact_menu(
        meal_options: Dict[str, Dict[str, List[Dict]]],
        snack_options: List[Dict]
    ):
        """
        Compact version - tanpa nutrition details
        """
        
        print("\n" + "="*60)
        print("PERSONALIZED MENU OPTIONS")
        print("="*60 + "\n")
        
        for meal_name in InteractiveMenuFormatter.MEALS_ORDER:
            
            if meal_name not in meal_options:
                continue
            
            meal_data = meal_options[meal_name]
            label = InteractiveMenuFormatter.MEAL_LABELS.get(meal_name, meal_name.upper())
            
            print(f"\n{label}:")
            
            for category in InteractiveMenuFormatter.CATEGORIES_ORDER:
                
                if category not in meal_data:
                    continue
                
                cat_label = InteractiveMenuFormatter.CATEGORY_LABELS.get(category, category.upper())
                options = meal_data[category]
                
                print(f"  {cat_label}:")
                
                for idx, option in enumerate(options, 1):
                    food_name = option.get('food_name', 'Unknown')
                    print(f"    {InteractiveMenuFormatter.CHECKBOX}  [{idx}] {food_name}")
        
        # Snacks
        if snack_options:
            print(f"\nSNACK:")
            for idx, snack in enumerate(snack_options, 1):
                food_name = snack.get('food_name', 'Unknown')
                print(f"  {InteractiveMenuFormatter.CHECKBOX}  [{idx}] {food_name}")
        
        print()
    
    @staticmethod
    def display_table_format(
        meal_options: Dict[str, Dict[str, List[Dict]]],
        snack_options: List[Dict]
    ):
        """
        Table format - untuk comparative view
        """
        
        print("\n" + "="*100)
        print("MENU OPTIONS - COMPARISON VIEW")
        print("="*100 + "\n")
        
        for meal_name in InteractiveMenuFormatter.MEALS_ORDER:
            
            if meal_name not in meal_options:
                continue
            
            meal_data = meal_options[meal_name]
            label = InteractiveMenuFormatter.MEAL_LABELS.get(meal_name, meal_name.upper())
            
            print(f"\n{label}")
            print("-"*100)
            
            # Create table per category
            for category in InteractiveMenuFormatter.CATEGORIES_ORDER:
                
                if category not in meal_data:
                    continue
                
                cat_label = InteractiveMenuFormatter.CATEGORY_LABELS.get(category, category.upper())
                options = meal_data[category]
                
                print(f"\n{cat_label}:")
                print(f"{'':4} | {'Food Name':<30} | {'Portion':>8} | {'Kcal':>6} | {'P':>5} | {'C':>5} | {'F':>5}")
                print("-"*80)
                
                for idx, option in enumerate(options, 1):
                    food_name = option.get('food_name', 'Unknown')
                    portion = option.get('portion', 0)
                    energy = option.get('energy_kcal', 0)
                    protein = option.get('protein_g', 0)
                    carbs = option.get('carbs_g', 0)
                    fat = option.get('fat_g', 0)
                    
                    print(f"[{idx}] | {food_name:<30} | {portion:>7.0f}g | {energy:>6.0f} | {protein:>5.1f} | {carbs:>5.1f} | {fat:>5.1f}")
        
        # Snacks
        if snack_options:
            print(f"\nSNACK")
            print(f"{'':4} | {'Food Name':<30} | {'Portion':>8} | {'Kcal':>6}")
            print("-"*60)
            
            for idx, snack in enumerate(snack_options, 1):
                food_name = snack.get('food_name', 'Unknown')
                portion = snack.get('portion', 0)
                energy = snack.get('energy_kcal', 0)
                
                print(f"[{idx}] | {food_name:<30} | {portion:>7.0f}g | {energy:>6.0f}")
        
        print()
    
    # ========================================================================
    # HELPER: Generate summary dari selection
    # ========================================================================
    
    @staticmethod
    def generate_selection_summary(
        selection: Dict[str, Dict[str, int]],
        meal_options: Dict[str, Dict[str, List[Dict]]],
        snack_options: List[Dict]
    ) -> Dict:
        """
        Generate summary data dari user selection
        
        Args:
            selection: {meal: {category: selected_index}, ...}
            Example: {'breakfast': {'main_course': 1, 'side_dish': 0, 'drink': 1}, ...}
        
        Returns:
            Summary dengan selected foods dan nutrition totals
        """
        
        summary = {
            'selected_foods': {},
            'daily_totals': {
                'energy_kcal': 0,
                'protein_g': 0,
                'carbs_g': 0,
                'fat_g': 0,
            },
            'meals': {}
        }
        
        for meal_name, categories_selection in selection.items():
            
            if meal_name not in meal_options:
                continue
            
            meal_summary = {
                'foods': {},
                'totals': {
                    'energy_kcal': 0,
                    'protein_g': 0,
                    'carbs_g': 0,
                    'fat_g': 0,
                }
            }
            
            for category, selected_idx in categories_selection.items():
                
                if category not in meal_options[meal_name]:
                    continue
                
                options = meal_options[meal_name][category]
                
                if selected_idx < 0 or selected_idx >= len(options):
                    continue
                
                selected_food = options[selected_idx]
                
                meal_summary['foods'][category] = selected_food
                
                # Add to meal totals
                meal_summary['totals']['energy_kcal'] += selected_food.get('energy_kcal', 0)
                meal_summary['totals']['protein_g'] += selected_food.get('protein_g', 0)
                meal_summary['totals']['carbs_g'] += selected_food.get('carbs_g', 0)
                meal_summary['totals']['fat_g'] += selected_food.get('fat_g', 0)
            
            summary['meals'][meal_name] = meal_summary
            
            # Add to daily totals
            summary['daily_totals']['energy_kcal'] += meal_summary['totals']['energy_kcal']
            summary['daily_totals']['protein_g'] += meal_summary['totals']['protein_g']
            summary['daily_totals']['carbs_g'] += meal_summary['totals']['carbs_g']
            summary['daily_totals']['fat_g'] += meal_summary['totals']['fat_g']
        
        return summary


if __name__ == "__main__":
    print("InteractiveMenuFormatter module loaded")
    print("Use: from interactive_menu_formatter import InteractiveMenuFormatter")
