"""
Validator untuk hard & soft constraints pada chromosome
"""

from typing import Dict, List, Tuple


class ChromosomeValidator:
    """Validate chromosome terhadap hard constraints"""
    
    @staticmethod
    def is_valid_chromosome(
        chromosome: List[int],
        candidates_data: Dict,
        guidelines: Dict,
        user_tdee: float,
        tolerance_calorie: Tuple[float, float] = (0.9, 1.1)
    ) -> Tuple[bool, str]:
        """
        Validate chromosome terhadap hard constraints
        
        Args:
            chromosome: [10 genes] dengan nilai 0-3
            candidates_data: Dict berisi food candidates per slot
            guidelines: Nutrient constraints dari NutritionService
            user_tdee: Target Daily Energy Expenditure
            tolerance_calorie: (min_multiplier, max_multiplier) untuk TDEE
                             default: (0.9, 1.1) berarti ±10%
        
        Returns:
            (is_valid: bool, error_msg: str)
        """
        
        # Constraint 1: Chromosome length harus 10
        if len(chromosome) != 10:
            return False, f"Chromosome length must be 10, got {len(chromosome)}"
        
        # Constraint 2: Setiap gene harus dalam range
        for i, gene in enumerate(chromosome):
            if not isinstance(gene, int) or gene < 0 or gene > 3:
                return False, f"Gene {i} has invalid value {gene}, must be in [0, 1, 2, 3]"
        
        # Constraint 3: Setiap slot harus punya candidate yang valid
        slot_names = [
            'breakfast_main', 'breakfast_side', 'breakfast_drink',
            'lunch_main', 'lunch_side', 'lunch_drink',
            'dinner_main', 'dinner_side', 'dinner_drink',
            'snack'
        ]
        
        for slot_idx, slot_name in enumerate(slot_names):
            gene_value = chromosome[slot_idx]
            
            # Check apakah candidates ada untuk slot ini
            slot_type = slot_name.rsplit('_', 1)[0]  # e.g., 'breakfast_main' -> 'breakfast'
            course_type = slot_name.split('_', 1)[1] if '_' in slot_name else 'snack'  # 'main'
            
            if slot_name == 'snack':
                if 'snack' not in candidates_data:
                    return False, f"No candidates for snack"
                if gene_value >= len(candidates_data['snack']):
                    return False, f"Invalid candidate index {gene_value} for snack"
            else:
                if slot_type not in candidates_data:
                    return False, f"No candidates for {slot_type}"
                if course_type not in candidates_data[slot_type]:
                    return False, f"No {course_type} candidates for {slot_type}"
                if gene_value >= len(candidates_data[slot_type][course_type]):
                    return False, f"Invalid candidate index {gene_value} for {slot_name}"
        
        # Constraint 4: Total calorie harus within tolerance
        total_calorie = ChromosomeValidator._calculate_total_calorie(
            chromosome, candidates_data
        )
        
        min_threshold = user_tdee * tolerance_calorie[0]
        max_threshold = user_tdee * tolerance_calorie[1]
        
        if not (min_threshold <= total_calorie <= max_threshold):
            return False, (
                f"Total calorie {total_calorie:.0f} out of bounds "
                f"[{min_threshold:.0f}, {max_threshold:.0f}]"
            )
        
        # Constraint 5: Critical nutrients max (e.g., sodium)
        # SOFT CONSTRAINT - handled in fitness, not here
        
        return True, ""
    
    @staticmethod
    def _calculate_total_calorie(chromosome: List[int], candidates_data: Dict) -> float:
        """Helper: Calculate total calorie dari chromosome"""
        total = 0.0
        
        slot_names = [
            'breakfast_main', 'breakfast_side', 'breakfast_drink',
            'lunch_main', 'lunch_side', 'lunch_drink',
            'dinner_main', 'dinner_side', 'dinner_drink',
            'snack'
        ]
        
        for slot_idx, slot_name in enumerate(slot_names):
            gene_value = chromosome[slot_idx]
            
            if slot_name == 'snack':
                if 'snack' in candidates_data and gene_value < len(candidates_data['snack']):
                    food = candidates_data['snack'][gene_value]
                    total += food.get('energy_kcal', 0)
            else:
                parts = slot_name.rsplit('_', 1)
                meal_type = parts[0]  # 'breakfast', 'lunch', 'dinner'
                course_type = parts[1]  # 'main', 'side', 'drink'
                
                if meal_type in candidates_data and course_type in candidates_data[meal_type]:
                    if gene_value < len(candidates_data[meal_type][course_type]):
                        food = candidates_data[meal_type][course_type][gene_value]
                        total += food.get('energy_kcal', 0)
        
        return total
    
    @staticmethod
    def repair_chromosome(
        chromosome: List[int],
        candidates_data: Dict,
        guidelines: Dict,
        user_tdee: float,
        max_attempts: int = 5
    ) -> List[int]:
        """
        Coba repair invalid chromosome dengan random regeneration
        
        Args:
            chromosome: Potentially invalid chromosome
            candidates_data: Food candidates
            guidelines: Nutrient constraints
            user_tdee: Target energy
            max_attempts: Max attempts untuk repair
        
        Returns:
            Repaired chromosome atau original jika tidak bisa di-repair
        """
        import random
        
        repaired = chromosome.copy()
        
        for attempt in range(max_attempts):
            is_valid, error_msg = ChromosomeValidator.is_valid_chromosome(
                repaired, candidates_data, guidelines, user_tdee
            )
            
            if is_valid:
                return repaired
            
            # Coba regenerate random genes
            for slot_idx in range(len(repaired)):
                if random.random() < 0.5:  # 50% chance to regenerate
                    # Count candidates for this slot
                    slot_names = [
                        'breakfast_main', 'breakfast_side', 'breakfast_drink',
                        'lunch_main', 'lunch_side', 'lunch_drink',
                        'dinner_main', 'dinner_side', 'dinner_drink',
                        'snack'
                    ]
                    
                    slot_name = slot_names[slot_idx]
                    
                    if slot_name == 'snack':
                        if 'snack' in candidates_data:
                            max_candidates = len(candidates_data['snack'])
                            repaired[slot_idx] = random.randint(0, max_candidates - 1)
                    else:
                        parts = slot_name.rsplit('_', 1)
                        meal_type = parts[0]
                        course_type = parts[1]
                        
                        if meal_type in candidates_data and course_type in candidates_data[meal_type]:
                            max_candidates = len(candidates_data[meal_type][course_type])
                            repaired[slot_idx] = random.randint(0, max_candidates - 1)
        
        # Return repaired even if still invalid (will be filtered later)
        return repaired

