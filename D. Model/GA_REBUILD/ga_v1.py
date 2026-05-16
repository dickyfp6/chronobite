"""
GENETIC ALGORITHM - Simple Implementation v1
============================================

Core GA engine untuk meal planning optimization.
Mencari kombinasi 10 makanan (10 gene chromosome) yang memenuhi
constraint nutrisi dengan penalty minimal.

Struktur Chromosome (10 items):
- 0: breakfast_main
- 1: breakfast_side
- 2: breakfast_drink
- 3: lunch_main
- 4: lunch_side
- 5: lunch_drink
- 6: dinner_main
- 7: dinner_side
- 8: dinner_drink
- 9: snack

Fitness = Total penalty terhadap nutrient constraints
GA Loop = Initialize → Evaluate → Select → Crossover → Mutate → Repeat

Tanpa class, hanya functions murni.
"""

import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional, cast

# ═════════════════════════════════════════════════════════════════════════════
# GUIDELINE UTILITIES - Consistency helpers
# ═════════════════════════════════════════════════════════════════════════════

def merge_hard_soft_guidelines(guidelines: Dict) -> Dict:
    """
    Merge HARD + SOFT guidelines menjadi flat dictionary untuk compatibility.
    
    Purpose: Memastikan constraint consistency antara GA dan final evaluation.
    Bug Fix: Mencegah guidelines berubah menjadi 0-inf di tahap akhir.
    
    Args:
        guidelines: Dict dengan struktur {'hard': {...}, 'soft': {...}} 
                   atau flat dict {nutrient: {...}}
    
    Returns:
        Dict flat: {nutrient: {min, max, ...}, ...}
    
    Example:
        SEBELUM (GA): {'hard': {'sodium_mg': {'min': 1500, 'max': 1500}},
                       'soft': {'protein_g': {'min': 60, 'max': 120}}}
        
        SESUDAH (Final): {'sodium_mg': {'min': 1500, 'max': 1500},
                          'protein_g': {'min': 60, 'max': 120}}
    """
    if not guidelines:
        return {}
    
    # Detect if already flat
    if isinstance(guidelines, dict):
        first_key = next(iter(guidelines.keys())) if guidelines else None
        if first_key:
            first_val = guidelines[first_key]
            # Check if value is dict with 'min/max' (flat structure) or nested 'hard/soft'
            if isinstance(first_val, dict) and ('min' in first_val or 'max' in first_val or 'constraint_type' in first_val):
                # Already flat
                return guidelines
    
    # Merge HARD + SOFT if nested
    guidelines_flat = {}
    
    if 'hard' in guidelines and isinstance(guidelines['hard'], dict):
        guidelines_flat.update(guidelines['hard'])
    
    if 'soft' in guidelines and isinstance(guidelines['soft'], dict):
        guidelines_flat.update(guidelines['soft'])
    
    return guidelines_flat if guidelines_flat else guidelines


def validate_final_solution(solution: pd.DataFrame, guidelines: Dict, tdee: Optional[float] = None) -> Dict:
    """
    Validate solusi final terhadap constraints yang SAMA dengan GA fitness function.
    
    Purpose: Ensure consistency antara GA evaluation dan final output validation.
    
    Args:
        solution: DataFrame selected meal plan (10 items)
        guidelines: Dict constraints (sama struktur dengan GA)
        tdee: Target daily energy expenditure (kcal)
    
    Returns:
        Dict validation result:
        {
            'is_valid': bool,
            'compliance_rate': float (0-100),
            'violations': [(nutrient, value, min, max, severity), ...],
            'summary': str
        }
    
    Example:
        result = validate_final_solution(selected_meal, guidelines, tdee=2206)
        if not result['is_valid']:
            print(f"Failed: {result['summary']}")
            for nutrient, val, min_val, max_val, sev in result['violations']:
                print(f"  {nutrient}: {val} (range {min_val}-{max_val}) - {sev}")
    """
    # Import disini untuk avoid circular dependency
    from ga_v1 import calculate_total_nutrition
    
    # Flatten guidelines
    guidelines_flat = merge_hard_soft_guidelines(guidelines)
    
    # Calculate total nutrition
    total_nutrition = calculate_total_nutrition(solution)
    
    violations = []
    compliant_count = 0
    total_checks = 0
    
    # Check setiap nutrient
    for nutrient, constraint in guidelines_flat.items():
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        if nutrient not in total_nutrition:
            continue
        
        value = total_nutrition[nutrient]
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        
        total_checks += 1
        
        if min_val <= value <= max_val:
            compliant_count += 1
        else:
            if value < min_val:
                severity = f"LOW (need {min_val - value:.1f} more)"
            else:
                severity = f"HIGH (excess {value - max_val:.1f})"
            
            violations.append((nutrient, value, min_val, max_val, severity))
    
    # Energy check jika ada TDEE
    if tdee and tdee > 0:
        current_energy = total_nutrition.get('energy_kcal', 0)
        min_energy = 0.75 * tdee
        max_energy = 1.25 * tdee
        
        total_checks += 1
        if min_energy <= current_energy <= max_energy:
            compliant_count += 1
        else:
            severity = f"{'LOW' if current_energy < min_energy else 'HIGH'} (need {abs(min_energy - current_energy) if current_energy < min_energy else abs(current_energy - max_energy):.0f} kcal)"
            violations.append(('energy_kcal', current_energy, min_energy, max_energy, severity))
    
    # Summary
    compliance_rate = (compliant_count / total_checks * 100) if total_checks > 0 else 0
    is_valid = len(violations) == 0
    
    summary = f"Compliance: {compliance_rate:.0f}% ({compliant_count}/{total_checks})"
    if not is_valid:
        summary += f" - {len(violations)} violations found"
    
    return {
        'is_valid': is_valid,
        'compliance_rate': compliance_rate,
        'violations': violations,
        'summary': summary
    }


# ═════════════════════════════════════════════════════════════════════════════
# DATA FILTERING - Remove junk food sebelum GA
# ═════════════════════════════════════════════════════════════════════════════

def filter_food_dataset(food_df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Filter food dataset untuk remove:
    1. Junk food (candy, chocolate, dessert, dll)
    2. Unrealistic items (energy < 50 kcal, energy > 500 kcal @ 100g)
    3. Pure fat/oil items
    
    Purpose: GA bekerja dengan makanan realistis, bukan junk food
    
    Args:
        food_df: Full dataset
        verbose: Print filtering stats
    
    Returns:
        Filtered DataFrame dengan hanya makanan berkualitas
    
    Filtering logic:
    1. Hapus junk food keywords
    2. Hapus energy ekstrim (< 50 atau > 500 kcal @ 100g)
    3. Hapus pure oil/fat items (fat > 90% of energy)
    """
    
    initial_count = len(food_df)
    
    # STEP 1: Remove junk food keywords
    junk_keywords = [
        'candy', 'chocolate', 'dessert', 'cake', 'cookie', 'syrup', 'donut',
        'candy bar', 'confection', 'sweet candy', 'caramel', 'fudge',
        'pie', 'ice cream', 'pudding', 'mousse', 'brownie', 'wafer',
        'candied', 'frosting', 'icing', 'glaze', 'cream cheese'
    ]
    junk_pattern = '|'.join(junk_keywords)
    
    filtered = food_df.copy()
    if 'food_name' in filtered.columns:
        filtered = cast(pd.DataFrame, filtered[
            ~filtered['food_name'].str.lower().str.contains(junk_pattern, na=False)
        ])
    
    junk_removed = initial_count - len(filtered)
    
    # STEP 2: Remove unrealistic energy values (per 100g)
    # Normal food @ 100g: 50-500 kcal (water-based to oil-based)
    filtered = cast(pd.DataFrame, filtered[
        (filtered['energy_kcal'] >= 50) &
        (filtered['energy_kcal'] <= 500)
    ])
    energy_removed = initial_count - junk_removed - len(filtered)
    
    # STEP 3: Remove pure oil/fat items
    # Fat provides 9 kcal/g, so if fat > energy/9 * 0.85 = mostly fat → exclude
    if 'fat_g' in filtered.columns and 'energy_kcal' in filtered.columns:
        filtered = cast(pd.DataFrame, filtered[
            filtered['fat_g'] <= (filtered['energy_kcal'] / 9 * 0.85)
        ])
    
    oil_removed = initial_count - junk_removed - energy_removed - len(filtered)
    
    if verbose:
        print(f"\n🧹 DATASET FILTERING:")
        print(f"   Initial items: {initial_count}")
        print(f"   - Junk food removed: {junk_removed}")
        print(f"   - Extreme energy removed: {energy_removed}")
        print(f"   - Pure fat/oil removed: {oil_removed}")
        print(f"   ────────────────────")
        print(f"   Final items: {len(filtered)} ({len(filtered)/initial_count*100:.1f}%)")
        print(f"   ✓ Dataset cleaned, ready for GA\n")
    
    return filtered


# ═════════════════════════════════════════════════════════════════════════════
# CHROMOSOME STRUCTURE
# ═════════════════════════════════════════════════════════════════════════════

CHROMOSOME_SIZE = 10
SLOT_NAMES = [
    'breakfast_main',    # 0
    'breakfast_side',    # 1
    'breakfast_drink',   # 2
    'lunch_main',        # 3
    'lunch_side',        # 4
    'lunch_drink',       # 5
    'dinner_main',       # 6
    'dinner_side',       # 7
    'dinner_drink',      # 8
    'snack'              # 9
]

MEAL_INDICES = {
    'breakfast': [0, 1, 2],  # main, side, drink
    'lunch': [3, 4, 5],      # main, side, drink
    'dinner': [6, 7, 8],     # main, side, drink
    'snack': [9]             # just 1 item
}

# Mapping slot ke expected consumption_label
# Digunakan untuk filter makanan sesuai kategori konsumsi yang realistis
# HARUS MATCH dengan actual dataset labels: "Main Course", "Side Dish", "Drink", "Snack"
SLOT_LABEL_MAP = {
    0: 'Main Course',    # breakfast_main
    1: 'Side Dish',      # breakfast_side
    2: 'Drink',          # breakfast_drink
    3: 'Main Course',    # lunch_main
    4: 'Side Dish',      # lunch_side
    5: 'Drink',          # lunch_drink
    6: 'Main Course',    # dinner_main
    7: 'Side Dish',      # dinner_side
    8: 'Drink',          # dinner_drink
    9: 'Snack'           # snack
}

# Legacy: kept for reference (tidak digunakan lagi, gunakan consumption_label)
SLOT_FOOD_GROUP_MAPPING = {
    0: ['main_course', 'staple', 'rice', 'bread'],           # breakfast_main
    1: ['side_dish', 'vegetable', 'protein', 'legume'],      # breakfast_side
    2: ['beverage', 'drink', 'juice', 'milk', 'tea'],        # breakfast_drink
    3: ['main_course', 'staple', 'rice', 'noodle'],          # lunch_main
    4: ['side_dish', 'vegetable', 'protein', 'legume'],      # lunch_side
    5: ['beverage', 'drink', 'juice', 'milk', 'tea'],        # lunch_drink
    6: ['main_course', 'staple', 'rice', 'noodle'],          # dinner_main
    7: ['side_dish', 'vegetable', 'protein', 'legume'],      # dinner_side
    8: ['beverage', 'drink', 'juice', 'milk', 'tea'],        # dinner_drink
    9: ['snack', 'dessert', 'fruit', 'nut']                  # snack
}

# Nutrient weights - semakin tinggi weight semakin strict constraint-nya
# SOFT CONSTRAINTS: Macronutrients (protein, carbs, fat) sangat penting - weight 2-3x
# HARD CONSTRAINTS: Disease-related (sodium, cholesterol) - akan di-multiply 10-15x lagi di fitness
NUTRIENT_WEIGHTS = {
    'energy_kcal': 2.0,           # Energy is critical (akan 50-30x di energy step)
    'protein_g': 2.5,             # SOFT: Protein sangat penting (3x karena fundamental)
    'carbohydrate_g': 2.0,        # SOFT: Carbs penting untuk energy (2x)
    'fat_g': 2.0,                 # SOFT: Fat penting untuk hormone & absorption (2x)
    'fiber_g': 1.5,               # SOFT: Fiber penting untuk digestive health
    'sodium_mg': 1.5,             # HARD: Akan di-multiply 10-15x lagi
    'calcium_mg': 1.2,            # SOFT/HARD: Bone health
    'iron_mg': 1.3,               # SOFT/HARD: Oxygen transport
    'phosphorus_mg': 1.0,         # HARD: Bone health (CKD)
    'zinc_mg': 1.0,               # SOFT: Immune function
    'potassium_mg': 1.5,          # HARD: Electrolyte balance (hypertension)
    'magnesium_mg': 1.0,          # SOFT: Muscle function
    'vitamin_a_iu': 0.8,          # SOFT: Vision (lower weight - optional)
    'vitamin_c_mg': 0.8,          # SOFT: Immune (lower weight)
    'vitamin_b1_mg': 0.8,         # SOFT: Energy metabolism (lower weight)
    'vitamin_b2_mg': 0.8,         # SOFT: Energy metabolism (lower weight)
    'vitamin_b3_mg': 0.8,         # SOFT: Energy metabolism (lower weight)
    'cholesterol_mg': 1.5         # HARD: Cardiovascular health - akan di-multiply 10-15x lagi
}

# Duplicate penalty weight
DUPLICATE_PENALTY_WEIGHT = 50.0  # Penalty for each duplicate food item


# ═════════════════════════════════════════════════════════════════════════════
# 1. RANDOM SOLUTION - Generate meal plan random
# ═════════════════════════════════════════════════════════════════════════════

def _filter_food_by_slot(food_df: pd.DataFrame, slot_idx: int, debug: bool = False) -> pd.DataFrame:
    """
    Filter food items sesuai dengan expected consumption_label untuk slot tertentu
    Menggunakan case-insensitive comparison untuk robustness
    
    Args:
        food_df: DataFrame berisi semua food items dengan kolom 'consumption_label'
        slot_idx: Index slot (0-9)
        debug: Jika True, print info tentang filtering
    
    Returns:
        Filtered DataFrame atau fallback jika tidak ada match
        
    Logic:
        - Cek apakah ada kolom 'consumption_label' di dalam food_df
        - Ambil expected_label dari SLOT_LABEL_MAP[slot_idx]
        - Filter dengan case-insensitive comparison + strip
        - Fallback: return sample max 20 items jika tidak ada match
    """
    # Jika tidak ada consumption_label column, return semua items
    if 'consumption_label' not in food_df.columns:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No consumption_label column")
        return food_df
    
    # Ambil expected label untuk slot ini
    expected_label = SLOT_LABEL_MAP.get(slot_idx, None)
    if not expected_label:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No label mapping")
        return food_df
    
    # Filter items yang match expected label (case-insensitive with strip)
    filtered = cast(pd.DataFrame, food_df[
        food_df['consumption_label'].str.strip().str.lower() == expected_label.lower()
    ])
    
    # ════════════════════════════════════════════════════════════════════════
    # QUALITY FILTER - Ensure only quality foods are selected
    # ════════════════════════════════════════════════════════════════════════
    # Apply quality checks (nutrient minimums, energy ranges, etc)
    filtered = _apply_quality_filter(filtered, expected_label)
    
    if debug:
        print(f"DEBUG: Slot {slot_idx} ({SLOT_NAMES[slot_idx]}) -> label='{expected_label}' -> {len(filtered)} items (after quality filter)")
        if len(filtered) == 0:
            print(f"       Available labels: {food_df['consumption_label'].unique().tolist()}")
    
    # Jika tidak ada match, sample dari original sebagai fallback
    if len(filtered) == 0:
        if debug:
            print(f"DEBUG: Slot {slot_idx} - No items found, using fallback (sampling max 20)")
        return food_df.sample(n=min(20, len(food_df)))
    
    return filtered


def random_solution(food_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 1 solusi random = 10 makanan random dari food_df dengan food group filter
    
    Chromosome structure:
    - Index 0-2: breakfast (main, side, drink)
    - Index 3-5: lunch (main, side, drink)
    - Index 6-8: dinner (main, side, drink)
    - Index 9: snack
    
    Args:
        food_df: DataFrame berisi semua food items (optional: dengan kolom 'food_group')
    
    Returns:
        DataFrame dengan 10 baris (1 item per slot)
    
    Logic:
        - Untuk setiap slot (0-9), filter foods by consumption_label
        - Jika food_df >= 10 items → sample tanpa replacement (unique)
        - Jika food_df < 10 items → sample dengan replacement (boleh duplikat)
    
    Example:
        solution = random_solution(food_df)
        # output: DataFrame dengan 10 rows
        #   food_name           food_group      energy_kcal  ...
        # 0  Nasi Putih          rice            180          ...
        # 1  Telur Goreng        protein         150          ...
        # 2  Teh Panas           beverage        50           ...
        # 3  Nasi Goreng         main_course     450          ...
        # ...
        # 9  Kue                 snack           100          ...
    """
    if len(food_df) < 1:
        raise ValueError(f"Food database harus memiliki minimal 1 item, got {len(food_df)}")
    
    solution_items = []
    used_foods = set()  # Track used food_name untuk menghindari duplikasi jika mungkin
    
    # Generate 1 item per slot dengan food group filter jika tersedia
    for slot_idx in range(CHROMOSOME_SIZE):
        filtered_df = _filter_food_by_slot(food_df, slot_idx)
        
        # Sample 1 item untuk slot ini
        # Karena n=1, parameter replace tidak relevan
        if len(filtered_df) > 0:
            # Coba hindari duplikasi jika ada pilihan lain
            available_df = filtered_df
            if 'food_name' in filtered_df.columns and len(used_foods) > 0:
                # Filter out foods yang sudah digunakan jika masih ada pilihan
                not_used = filtered_df[~filtered_df['food_name'].isin(used_foods)]
                if len(not_used) > 0:
                    available_df = not_used
            
            item = available_df.sample(n=1)
            solution_items.append(item)
            
            # Track food yang digunakan
            if 'food_name' in item.columns:
                food_name = item.iloc[0].get('food_name', '')
                if food_name:
                    used_foods.add(food_name)
    
    # Concat semua items dan reset index
    if solution_items:
        solution = pd.concat(solution_items, ignore_index=True)
    else:
        # Fallback: jika semua filter gagal, random sample saja
        # Jika food_df < 10 items, allow replacement untuk mencapai 10 items
        allow_replacement = len(food_df) < CHROMOSOME_SIZE
        solution = food_df.sample(n=CHROMOSOME_SIZE, replace=allow_replacement).reset_index(drop=True)
    
    return solution


# ═════════════════════════════════════════════════════════════════════════════
# 2. CALCULATE TOTAL NUTRITION - Sum nutrisi dari 10 item (chromosome)
# ═════════════════════════════════════════════════════════════════════════════

def calculate_total_nutrition(solution: pd.DataFrame) -> Dict[str, float]:
    """
    Hitung total nutrisi dari 10 item dalam solution (chromosome)
    
    Args:
        solution: DataFrame dengan 10 baris (10 items dari chromosome)
    
    Returns:
        Dict: {nutrient_name: total_value, ...}
        Contoh: {'energy_kcal': 1850, 'protein_g': 65, 'fat_g': 45, ...}
    
    Method:
        - Sum semua numeric columns di solution
        - Ignore non-numeric columns
    """
    # Sum semua numeric columns (otomatis)
    total_nutrition = solution.select_dtypes(include=[np.number]).sum().to_dict()
    return total_nutrition


# ═════════════════════════════════════════════════════════════════════════════
# 3. FITNESS - Hitung penalty score dari nutrient violations
# ═════════════════════════════════════════════════════════════════════════════

def fitness(solution: pd.DataFrame, guidelines: Dict, tdee: Optional[float] = None) -> float:
    """
    Hitung fitness score (penalty total) untuk 1 solusi (10-item chromosome)
    Dengan HARD dan SOFT constraints, weighted nutrients, duplicate penalty, dan normalization
    
    ⚠️  HARD vs SOFT (PERUBAHAN PHASE 4 - STRICT ENFORCEMENT):
        HARD (PRIMARY - disease-based + energy) - STRICT ENFORCEMENT:
            - Jika melanggar → REJECT LANGSUNG (return 1e9)
            - Toleransi: 5% (agar GA tidak stuck dengan dataset terbatas)
            - Contoh sodium: min=1500 → lower_bound=1425, upper_bound=1575
            - Jika value < 1425 atau value > 1575 → reject (return 1e9)
            - ENERGY: ±25% tolerance (0.75-1.25 × TDEE) - juga strict!
            - Sodium, Cholesterol, dll: HARUS dipenuhi (constraint medis!)
        
        SOFT (SECONDARY - DRI-based) - PENALTY-BASED:
            - Violation masih dihitung penalty seperti sebelumnya
            - Lebih fleksibel, tidak kritis
            - Protein, Carbs, Fat, Fiber: 10x multiplier (fundamental)
            - Micronutrients: 2x multiplier (flexible)
    
    Args:
        solution: DataFrame dengan 10 items (chromosome)
        guidelines: Dict struktur:
                   {
                       'hard': {nutrient: {'min': float, 'max': float, ...}, ...},
                       'soft': {nutrient: {'min': float, 'max': float, ...}, ...}
                   }
        tdee: Target daily energy expenditure (kcal) - untuk energy constraint
    
    Returns:
        float: Total penalty (semakin kecil = semakin baik)
                OR 1e9 jika ada HARD constraint violation (reject)
    """
    # Hitung total nutrisi dari solution
    total_nutrition = calculate_total_nutrition(solution)
    
    # ════════════════════════════════════════════════════════════════════════
    # SCALE NUTRITION TO TDEE (Konsistensi dengan tahap akhir portion sizing)
    # ════════════════════════════════════════════════════════════════════════
    # GA harus mengevaluasi seolah-olah sudah di-scale ke TDEE
    # Ini memastikan hasil GA konsisten dengan output akhir setelah portion scaling
    # 
    # Logic:
    #   - Ambil total energy dari solution (per 100g setiap item)
    #   - Hitung scale_factor = tdee / total_energy
    #   - Kalikan semua nutrient dengan scale_factor
    # 
    # Hasil:
    #   - GA menilai solusi dengan nilai yang sudah di-scale
    #   - Energy akan mendekati TDEE
    #   - Constraint akan lebih konsisten dengan output akhir
    if tdee and tdee > 0:
        total_energy = total_nutrition.get('energy_kcal', 0)
        if total_energy > 0:
            scale_factor = tdee / total_energy
            # Kalikan semua nutrient dengan scale factor
            # ⚠️  PENTING: Scaling berlaku ke SEMUA nutrient, bukan hanya energy!
            for nutrient_name in total_nutrition:
                total_nutrition[nutrient_name] = total_nutrition[nutrient_name] * scale_factor
    
    total_penalty = 0.0
    constraint_count = 0
    
    # ════════════════════════════════════════════════════════════════════════
    # DETECT GUIDELINE STRUCTURE (HARD/SOFT atau LAMA)
    # ════════════════════════════════════════════════════════════════════════
    has_hard_soft = isinstance(guidelines.get(list(guidelines.keys())[0] if guidelines else None, None), dict) \
                    and 'hard' in guidelines and 'soft' in guidelines
    
    if has_hard_soft:
        hard_constraints = guidelines['hard']
        soft_constraints = guidelines['soft']
    else:
        # Backward compatibility: semua jadi SOFT
        hard_constraints = {}
        soft_constraints = guidelines
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 1: ENERGY CONSTRAINT - STRICT ENFORCEMENT (HARD)
    # ════════════════════════════════════════════════════════════════════════
    # Energy adalah CRITICAL - tanpa energy yang cukup, semua nutrient jadi irrelevant
    # Jika melanggar → REJECT LANGSUNG (return 1e9)
    # Tolerance ketat: 75% - 125% dari TDEE (±25%)
    if tdee and tdee > 0:
        current_energy = total_nutrition.get('energy_kcal', 0)
        
        # Ketat: 75% - 125% dari TDEE
        min_energy = 0.75 * tdee
        max_energy = 1.25 * tdee
        
        # ⚠️  STRICT ENFORCEMENT: Jika melanggar energy range → REJECT
        if current_energy < min_energy or current_energy > max_energy:
            return 1e9  # HARD violation - energy CRITICAL!
        
        constraint_count += 1
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 2: HARD CONSTRAINTS - SEMI-STRICT ENFORCEMENT (PENALTY SANGAT BESAR)
    # ════════════════════════════════════════════════════════════════════════
    # HARD constraint adalah constraint MEDIS - SANGAT DIPRIORITASKAN!
    # Jika melanggar → penalty SANGAT BESAR (10000x) tapi GA tetap bisa jalan
    # Multiplier 10000 >> SOFT multiplier (10-100) → HARD diprioritaskan
    # Tapi tidak return 1e9 agar GA bisa membandingkan & improve solusi antar generasi
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in hard_constraints.items():
        # Skip unlimited
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Skip jika nutrient tidak ada
        if nutrient_name not in total_nutrition:
            continue
        
        # Skip energy (sudah di-handle di STEP 1)
        if nutrient_name == 'energy_kcal':
            continue
        
        constraint_count += 1
        
        # Ambil nilai min dan max
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        # ⚠️  SEMI-STRICT: Penalty sangat besar (10000) tapi tidak reject
        # Multiplier 10000 jauh lebih besar daripada SOFT (10-100)
        # Hasil: HARD constraint prioritas tinggi tapi GA bisa jalan
        hard_multiplier = 10000
        
        if value < min_val:
            # Under minimum: penalty = (deficit) * 10000
            penalty = (min_val - value) * hard_multiplier
            total_penalty += penalty
        elif value > max_val:
            # Over maximum: penalty = (excess) * 10000
            penalty = (value - max_val) * hard_multiplier
            total_penalty += penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 3: SOFT CONSTRAINTS - PRIORITIZE MACRONUTRIENTS
    # Macronutrients (protein, carbs, fat) adalah TARGET UTAMA GA!
    # Gunakan penalty multipliers berbeda untuk setiap macro
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in soft_constraints.items():
        # Skip unlimited
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Skip jika nutrient tidak ada
        if nutrient_name not in total_nutrition:
            continue
        
        # Skip energy (sudah di-handle di STEP 1)
        if nutrient_name == 'energy_kcal':
            continue
        
        constraint_count += 1
        
        # Ambil nilai min dan max
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition[nutrient_name]
        
        # [NEW] MACRONUTRIENT-SPECIFIC PENALTIES
        # Carbohydrate: paling prioritas (800 deficit, 400 excess)
        # Fat: prioritas tinggi (600 deficit, 300 excess)
        # Protein: kontrol excess (500 excess, 200 deficit)
        # Lainnya: weight normal 2x
        
        if nutrient_name == 'carbohydrate_g':
            # CARBS - HIGHEST PRIORITY
            if value < min_val:
                penalty = (min_val - value) * 800
                total_penalty += penalty
            elif value > max_val:
                penalty = (value - max_val) * 400
                total_penalty += penalty
        
        elif nutrient_name == 'fat_g':
            # FAT - HIGH PRIORITY
            if value < min_val:
                penalty = (min_val - value) * 600
                total_penalty += penalty
            elif value > max_val:
                penalty = (value - max_val) * 300
                total_penalty += penalty
        
        elif nutrient_name == 'protein_g':
            # PROTEIN - CONTROL EXCESS, MAINTAIN MINIMUM
            if value < min_val:
                penalty = (min_val - value) * 200
                total_penalty += penalty
            elif value > max_val:
                penalty = (value - max_val) * 500  # Tinggi penalty untuk excess
                total_penalty += penalty
        
        else:
            # FIBER & MICRONUTRIENTS - FLEXIBLE (2x multiplier)
            weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
            soft_multiplier = 2.0
            
            if value < min_val:
                penalty = (min_val - value) * weight * soft_multiplier
                total_penalty += penalty
            elif value > max_val:
                penalty = (value - max_val) * weight * soft_multiplier
                total_penalty += penalty
    # ════════════════════════════════════════════════════════════════════════
    # STEP 4: DUPLICATE PENALTY
    # ════════════════════════════════════════════════════════════════════════
    if 'food_name' in solution.columns:
        unique_foods = solution['food_name'].nunique()
        duplicate_count = len(solution) - unique_foods
        duplicate_penalty = duplicate_count * DUPLICATE_PENALTY_WEIGHT
        total_penalty += duplicate_penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 5: RETURN PENALTY (NO NORMALIZATION!)
    # ════════════════════════════════════════════════════════════════════════
    # ⚠️  REMOVED normalisasi penalty (total_penalty / constraint_count)
    # Alasan: Normalisasi membuat penalty sangat kecil, GA abaikan constraint
    # Contoh: 1000 penalty ÷ 30 constraints = 33.33 (tidak signifikan!)
    # Solusi: Keep absolute penalty agar GA hindari violation
    
    return total_penalty


# ═════════════════════════════════════════════════════════════════════════════
# 4. CROSSOVER - Single-point crossover antara 2 parent
# ═════════════════════════════════════════════════════════════════════════════

def crossover(parent1: pd.DataFrame, parent2: pd.DataFrame) -> pd.DataFrame:
    """
    Single-point crossover: ambil N genes dari parent1, sisa dari parent2
    
    Args:
        parent1: Solution (DataFrame 10 rows)
        parent2: Solution (DataFrame 10 rows)
    
    Returns:
        Child: DataFrame hasil kombinasi parent1 + parent2
    
    Method:
        1. Random pilih crossover point (1-9)
           point = 3 → child = [P1[0:3] + P2[3:10]]
           point = 6 → child = [P1[0:6] + P2[6:10]]
        2. Konkatenasi dan reset index
    
    Example:
        P1 = [A,B,C,D,E,F,G,H,I,J]
        P2 = [1,2,3,4,5,6,7,8,9,10]
        
        Point = 3:
        Child = [A,B,C] + [4,5,6,7,8,9,10] = [A,B,C,4,5,6,7,8,9,10]
    """
    # Ensure size = 10
    assert len(parent1) == CHROMOSOME_SIZE, f"Parent1 harus {CHROMOSOME_SIZE} rows"
    assert len(parent2) == CHROMOSOME_SIZE, f"Parent2 harus {CHROMOSOME_SIZE} rows"
    
    # Random crossover point (1-9, tidak 0 atau 10)
    point = random.randint(1, CHROMOSOME_SIZE - 1)
    
    # Ambil N genes dari parent1, sisa dari parent2
    child_p1 = parent1.iloc[:point].copy()
    child_p2 = parent2.iloc[point:].copy()
    
    # Gabung - explicit cast to DataFrame untuk type checker
    concatenated = pd.concat([child_p1, child_p2], ignore_index=True)
    result = cast(pd.DataFrame, concatenated)
    
    return result


# ═════════════════════════════════════════════════════════════════════════════
# 5. MUTATION - Ganti 1 item random dengan makanan baru
# ═════════════════════════════════════════════════════════════════════════════

def mutation(solution: pd.DataFrame, food_df: pd.DataFrame, 
             mutation_rate: float = 0.3,
             guidelines: Optional[Dict] = None,
             tdee: Optional[float] = None) -> pd.DataFrame:
    """
    [GUIDED MUTATION - ENHANCED] Mutasi 2-3 genes dengan nutrient-aware selection
    
    Intelligently selects foods based on deficient macronutrients:
    - If carbs deficient: seek carb >= 20g AND protein <= 15g (avoid protein-heavy)
    - If fats deficient: seek fat >= 10g AND protein <= 15g (avoid protein-heavy)
    - If protein excess: seek protein <= 10g (low protein options)
    - Else: balanced selection
    
    Args:
        solution: DataFrame (10 rows) meal plan
        food_df: Available food items
        mutation_rate: Probability mutation (0.3 = 30%)
        guidelines: Optional constraints
        tdee: Optional tdee
    
    Returns:
        Mutated solution or original if no mutation
    """
    if random.random() > mutation_rate:
        return solution.copy()
    
    result = solution.copy()
    
    # Calculate current nutrient totals
    total_carb = solution['carbohydrate_g'].sum() if 'carbohydrate_g' in solution.columns else 0
    total_fat = solution['fat_g'].sum() if 'fat_g' in solution.columns else 0
    total_protein = solution['protein_g'].sum() if 'protein_g' in solution.columns else 0
    
    # Extract targets dari guidelines atau use defaults
    target_carb_min = 200
    target_fat_min = 50
    target_protein_max = 120
    
    if guidelines:
        guidelines_flat = {}
        if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
            guidelines_flat = {**guidelines['hard'], **guidelines['soft']}
        else:
            guidelines_flat = guidelines if isinstance(guidelines, dict) else {}
        
        if 'carbohydrate_g' in guidelines_flat:
            target_carb_min = guidelines_flat['carbohydrate_g'].get('min', target_carb_min)
        if 'fat_g' in guidelines_flat:
            target_fat_min = guidelines_flat['fat_g'].get('min', target_fat_min)
        if 'protein_g' in guidelines_flat:
            target_protein_max = guidelines_flat['protein_g'].get('max', target_protein_max)
    
    # Determine nutrient needs
    need_carb = total_carb < target_carb_min
    need_fat = total_fat < target_fat_min
    too_much_protein = total_protein > target_protein_max
    
    # Mutate 2-3 random genes untuk diversity
    num_mutations = random.randint(2, 3)
    genes_to_mutate = random.sample(range(CHROMOSOME_SIZE), min(num_mutations, CHROMOSOME_SIZE))
    
    for gene_idx in genes_to_mutate:
        # Apply slot filter (mandatory - maintain meal structure)
        slot_filtered = _filter_food_by_slot(food_df, gene_idx)
        candidate = slot_filtered.copy() if len(slot_filtered) > 0 else food_df.copy()
        
        # [ENHANCED] INTELLIGENT NUTRIENT-BASED FILTERING
        # Goal: Guide GA toward balanced nutrition, not just filling deficits
        
        if need_carb and 'carbohydrate_g' in candidate.columns and 'protein_g' in candidate.columns:
            # NEED CARBS: Seek high-carb, moderate-protein foods
            # Avoid protein-heavy foods that would unbalance the meal
            high_carb_balanced = candidate[
                (candidate['carbohydrate_g'] >= 20) &  # High carb
                (candidate['protein_g'] <= 15)           # Moderate protein (avoid protein-heavy)
            ]
            if len(high_carb_balanced) > 0:
                candidate = high_carb_balanced
            else:
                # Fallback: just high carb if no balanced option
                high_carb_only = candidate[candidate['carbohydrate_g'] >= 20]
                if len(high_carb_only) > 0:
                    candidate = high_carb_only
        
        elif need_fat and 'fat_g' in candidate.columns and 'protein_g' in candidate.columns:
            # NEED FAT: Seek high-fat, moderate-protein foods
            # Avoid protein-heavy options
            high_fat_balanced = candidate[
                (candidate['fat_g'] >= 10) &            # High fat
                (candidate['protein_g'] <= 15)          # Moderate protein (avoid protein-heavy)
            ]
            if len(high_fat_balanced) > 0:
                candidate = high_fat_balanced
            else:
                # Fallback: just high fat if no balanced option
                high_fat_only = candidate[candidate['fat_g'] >= 10]
                if len(high_fat_only) > 0:
                    candidate = high_fat_only
        
        elif too_much_protein and 'protein_g' in candidate.columns:
            # TOO MUCH PROTEIN: Seek low-protein options ONLY
            # This is CRITICAL to reduce protein excess
            low_protein = candidate[candidate['protein_g'] <= 10]
            if len(low_protein) > 0:
                candidate = low_protein
            # If no low-protein, still use candidate as-is (slot-filtered)
        
        # Select new food dari candidate dengan fallback strategy
        if len(candidate) > 0:
            new_food = candidate.sample(n=1).reset_index(drop=True)
        elif len(slot_filtered) > 0:
            new_food = slot_filtered.sample(n=1).reset_index(drop=True)
        else:
            new_food = food_df.sample(n=1).reset_index(drop=True)
        
        result.iloc[gene_idx] = new_food.iloc[0]
    
    return result


# ═════════════════════════════════════════════════════════════════════════════
# 6. RUN_GA - Main GA loop
# ═════════════════════════════════════════════════════════════════════════════

def run_ga(
    food_df: pd.DataFrame,
    guidelines: Dict,
    tdee: Optional[float] = None,
    generations: int = 50,
    pop_size: int = 20,
    elite_ratio: float = 0.25,
    mutation_rate: float = 0.3,
    verbose: bool = True
) -> Tuple[pd.DataFrame, List[pd.DataFrame]]:
    """
    Jalankan Genetic Algorithm untuk mencari optimal meal plan
    
    Args:
        food_df: DataFrame semua food items
        guidelines: Dict constraints dari NutritionService
        tdee: Target daily energy expenditure (kcal) - CRITICAL HARD constraint
        generations: Jumlah generasi (default 50)
        pop_size: Ukuran populasi (default 20)
        elite_ratio: Fraksi elite untuk breeding (default 0.25 = top 25%)
        mutation_rate: Probability mutasi (default 0.3 = 30%)
        verbose: Print progress? (default True)
    
    Returns:
        Tuple: (best_solution, top_solutions)
               best_solution: DataFrame optimal meal plan terbaik
               top_solutions: List[DataFrame] 10 solusi terbaik untuk generate options
    
    Algorithm:
        For gen in generations:
            1. Evaluate: hitung fitness semua population
            2. Sort ascending (kecil = baik)
            3. Elite: ambil top elite_ratio
            4. Breeding: loop sampai pop_size
               - Random select 2 parent dari elite
               - Crossover → child
               - Mutation(prob=mutation_rate)
            5. Update population
        
        Return: best individual + top 10 solutions dari semua generasi
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"GENETIC ALGORITHM - MEAL PLANNING OPTIMIZATION")
        print(f"{'='*70}")
        print(f"Pop Size: {pop_size} | Generations: {generations}")
        print(f"Elite Ratio: {elite_ratio} | Mutation Rate: {mutation_rate}")
        print(f"Food Items: {len(food_df)} | Constraints: {len(guidelines)}")
        if tdee:
            print(f"Target TDEE: {tdee:.0f} kcal/day (HARD constraint)")
        print(f"{'='*70}\n")
    
    # STEP 1: Initialize populasi random
    if verbose:
        print("[STEP 1] Initializing population...")
    
    population = []
    for _ in range(pop_size):
        solution = random_solution(food_df)
        population.append(solution)
    
    # Track best solution ever found
    best_solution = population[0].copy()
    best_fitness = fitness(best_solution, guidelines, tdee=tdee)
    
    # STEP 2: Main GA loop
    if verbose:
        print(f"[STEP 2] Running {generations} generations...")
        print(f"{'Gen':<5} | {'Best Fitness':<15} | {'Avg Fitness':<15}")
        print(f"{'-'*50}")
    
    for gen in range(generations):
        # 2a. Evaluate fitness semua population
        fitness_scores = []
        for solution in population:
            score = fitness(solution, guidelines, tdee=tdee)
            fitness_scores.append(score)
        
        # 2b. Sort population by fitness (ascending = semakin kecil semakin baik)
        sorted_indices = np.argsort(fitness_scores)
        population = [population[i] for i in sorted_indices]
        fitness_scores = [fitness_scores[i] for i in sorted_indices]
        
        # 2c. Track best solution
        if fitness_scores[0] < best_fitness:
            best_fitness = fitness_scores[0]
            best_solution = population[0].copy()
        
        # 2d. Show progress
        if verbose and (gen % max(1, generations // 10) == 0 or gen == generations - 1):
            avg_fitness = np.mean(fitness_scores)
            print(f"{gen:<5} | {fitness_scores[0]:<15.2f} | {avg_fitness:<15.2f}")
        
        # 2e. Selection: ambil elite
        elite_size = max(1, int(pop_size * elite_ratio))
        elite = population[:elite_size]
        
        # 2f. Breeding: buat populasi baru sampai pop_size
        new_population = elite.copy()  # Keep elite
        
        while len(new_population) < pop_size:
            # Select 2 parent dari elite (random with replacement)
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            
            # Crossover
            child = crossover(parent1, parent2)
            
            # Mutation (probabilitas mutation_rate)
            # [ENHANCED] Pass guidelines & tdee untuk guided nutrient-based mutation
            child = mutation(child, food_df, mutation_rate=mutation_rate, 
                           guidelines=guidelines, tdee=tdee)
            
            # Add to new population
            new_population.append(child)
        
        # Update population
        population = new_population[:pop_size]
        
        # [ENHANCED] Random injection untuk maintain diversity & prevent stagnation
        # Inject 2 random solutions setiap generasi untuk fresh genetic material
        if len(population) >= 2:
            population[-2:] = [random_solution(food_df) for _ in range(2)]
        
        # [ENHANCED] Shuffle population untuk avoid local convergence
        random.shuffle(population)
    
    # STEP 3: Final evaluation dan get top solutions
    if verbose:
        print(f"{'='*50}")
        print(f"[STEP 3] GA Complete!")
        print(f"Best Fitness Score: {best_fitness:.2f}")
    
    # Evaluate final population
    final_fitness_scores = []
    for solution in population:
        score = fitness(solution, guidelines, tdee=tdee)
        final_fitness_scores.append(score)
    
    # Sort population by fitness
    sorted_indices = np.argsort(final_fitness_scores)
    sorted_population = [population[i] for i in sorted_indices]
    sorted_scores = [final_fitness_scores[i] for i in sorted_indices]
    
    # Get top 10 solutions (atau kurang jika pop_size < 10)
    num_top_solutions = min(10, len(sorted_population))
    top_solutions = sorted_population[:num_top_solutions]
    
    if verbose:
        print(f"Top {num_top_solutions} solutions selected for options")
        print(f"{'='*50}\n")
    
    return best_solution, top_solutions


# ═════════════════════════════════════════════════════════════════════════════
# 7. LOCAL SEARCH - Fine-tuning setelah GA untuk memperbaiki solusi locally
# ═════════════════════════════════════════════════════════════════════════════

def local_search(
    solution: pd.DataFrame,
    food_df: pd.DataFrame,
    guidelines: Dict,
    tdee: Optional[float] = None,
    iterations: int = 20,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Local Search (Hill Climbing) dengan GUIDED + RESTRICTED CANDIDATE SELECTION
    
    Tujuan: Fine-tune GA result dengan mengganti makanan untuk menutup nutrient gaps
    
    Algoritma IMPROVED:
        1. TASK 1: Filter food_df - Remove junk foods (spices, powder, sauce, etc)
        2. TASK 2: Guided selection dengan PRIORITAS (fat > carb > protein)
        3. TASK 3: Smart gene selection (pilih gene dengan deficit terbesar, bukan random)
        4. TASK 4: Soft acceptance (accept jika nutrient improvement, tidak hanya fitness)
        5. TASK 5: Stop condition (break jika 5 iterasi tanpa improvement)
    
    Args:
        solution: GA result (DataFrame 10 items)
        food_df: Food database (DataFrame all items)
        guidelines: Dict constraints
        tdee: Target daily energy (optional)
        iterations: Max iterations (default 20)
        verbose: Print progress? (default False)
    
    Returns:
        DataFrame: Best solution ditemukan
    
    Expected Impact:
        - Carbs: +5 to +30g
        - Fats: +3 to +15g
        - Protein: -5 to -20g
        - Improvements: 5-8 per 20 iterations
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"LOCAL SEARCH - Guided Fine-tuning GA Result")
        print(f"{'='*70}")
    
    # ════════════════════════════════════════════════════════════════
    # TASK 1: FILTER KANDIDAT MAKANAN - Remove junk foods, spices, dll
    # ════════════════════════════════════════════════════════════════
    
    invalid_keywords = [
        'spice', 'powder', 'yeast', 'sauce', 'extract',
        'flavoring', 'dressing', 'seasoning', 'mix', 'condiment'
    ]
    
    # Buat cleaned dataset
    food_df_clean = food_df[
        ~food_df['food_name'].str.lower().str.contains('|'.join(invalid_keywords), na=False)
    ].copy()
    
    if verbose:
        print(f"[TASK 1] Candidate filtering:")
        print(f"  Original: {len(food_df)} items")
        print(f"  Cleaned: {len(food_df_clean)} items (removed {len(food_df) - len(food_df_clean)} junk foods)")
    
    if len(food_df_clean) < CHROMOSOME_SIZE:
        if verbose:
            print(f"  ⚠️ Warning: Too few clean candidates, using original dataset")
        food_df_clean = food_df.copy()
    
    # Start dengan GA solution
    best_solution = solution.copy()
    best_fitness = fitness(best_solution, guidelines, tdee=tdee)
    
    # Get guidelines
    guidelines_flat = merge_hard_soft_guidelines(guidelines)
    
    # Extract targets
    carb_target = guidelines_flat.get('carbohydrate_g', {}).get('max', 350)
    fat_target = guidelines_flat.get('fat_g', {}).get('max', 78)
    protein_target = guidelines_flat.get('protein_g', {}).get('max', 100)
    
    if verbose:
        print(f"\n[TARGETS] Macronutrients:")
        print(f"  Carbs: {carb_target:.0f}g")
        print(f"  Fats: {fat_target:.0f}g")
        print(f"  Protein: {protein_target:.0f}g\n")
    
    improvements = 0
    no_improve_count = 0
    max_no_improve = 5
    replacements = []
    
    iteration = 0
    while iteration < iterations and no_improve_count < max_no_improve:
        iteration += 1
        
        # ════════════════════════════════════════════════════════════════
        # TASK 2 & 3: Detect deficits + SMART GENE SELECTION
        # ════════════════════════════════════════════════════════════════
        
        current_nutrition = calculate_total_nutrition(best_solution)
        current_carbs = current_nutrition.get('carbohydrate_g', 0)
        current_fats = current_nutrition.get('fat_g', 0)
        current_protein = current_nutrition.get('protein_g', 0)
        
        carb_deficit = carb_target - current_carbs
        fat_deficit = fat_target - current_fats
        protein_excess = current_protein - protein_target
        
        # ════════ TASK 3: Smart Gene Selection (Not Random!) ════════
        # Pilih gene dengan deficit terbesar, bukan random
        
        selected_gene_idx = None
        selection_reason = None
        
        # PRIORITAS: Fat > Carb > Protein
        
        # PRIORITAS 1: Jika FAT deficit
        if fat_deficit > 3:  # Only if deficient
            # Cari gene dengan FAT TERENDAH
            fat_values = best_solution['fat_g'].values
            selected_gene_idx = np.argmin(fat_values)
            selection_reason = f"LOW FAT (deficit {fat_deficit:.1f}g)"
        
        # PRIORITAS 2: Jika CARB deficit (dan fat OK)
        elif carb_deficit > 5:  # Only if deficient
            # Cari gene dengan CARB TERENDAH
            carb_values = best_solution['carbohydrate_g'].values
            selected_gene_idx = np.argmin(carb_values)
            selection_reason = f"LOW CARB (deficit {carb_deficit:.1f}g)"
        
        # PRIORITAS 3: Jika PROTEIN excess
        elif protein_excess > 10:  # Only if excess
            # Cari gene dengan PROTEIN TERTINGGI
            protein_values = best_solution['protein_g'].values
            selected_gene_idx = np.argmax(protein_values)
            selection_reason = f"HIGH PROTEIN (excess {protein_excess:.1f}g)"
        
        # Fallback: Random gene
        else:
            selected_gene_idx = random.randint(0, len(best_solution) - 1)
            selection_reason = "EXPLORATORY"
        
        gene_idx = selected_gene_idx
        current_food = best_solution.iloc[gene_idx]
        current_food_name = current_food.get('food_name', 'Unknown')
        
        # ════════════════════════════════════════════════════════════════
        # TASK 2: GUIDED CANDIDATE SELECTION dengan PRIORITAS
        # ════════════════════════════════════════════════════════════════
        
        slot_name = SLOT_NAMES[gene_idx]
        expected_label = SLOT_LABEL_MAP.get(gene_idx, 'Main Course')
        
        # Filter by consumption label
        candidates = food_df_clean[food_df_clean['consumption_label'] == expected_label].copy()
        
        if len(candidates) == 0:
            no_improve_count += 1
            continue
        
        # GUIDED SELECTION dengan PRIORITAS STRICT
        # PRIORITAS: FAT > CARB > PROTEIN
        
        candidates_original_count = len(candidates)
        
        if fat_deficit > 3:
            # PRIORITAS 1: High fat
            high_fat = candidates[candidates['fat_g'] >= 10].copy()
            if len(high_fat) > 0:
                candidates = high_fat
        elif carb_deficit > 5:
            # PRIORITAS 2: High carb
            high_carb = candidates[candidates['carbohydrate_g'] >= 25].copy()
            if len(high_carb) > 0:
                candidates = high_carb
        elif protein_excess > 10:
            # PRIORITAS 3: Low protein
            low_protein = candidates[candidates['protein_g'] <= 10].copy()
            if len(low_protein) > 0:
                candidates = low_protein
        
        if len(candidates) == 0:
            no_improve_count += 1
            if verbose:
                print(f"[ITER {iteration}] No candidates found for {slot_name} ({selection_reason})")
            continue
        
        # Pilih random dari candidates yang sudah di-filter
        new_food = candidates.sample(n=1).iloc[0]
        new_food_name = new_food.get('food_name', 'Unknown')
        
        # Test replacement
        test_solution = best_solution.copy()
        test_solution.iloc[gene_idx] = new_food
        test_fitness = fitness(test_solution, guidelines, tdee=tdee)
        
        # ════════════════════════════════════════════════════════════════
        # TASK 4: SOFT ACCEPTANCE CRITERIA (Not just fitness improvement)
        # ════════════════════════════════════════════════════════════════
        
        test_nutrition = calculate_total_nutrition(test_solution)
        test_carbs = test_nutrition.get('carbohydrate_g', 0)
        test_fats = test_nutrition.get('fat_g', 0)
        test_protein = test_nutrition.get('protein_g', 0)
        
        # Cek apakah ada nutrient improvement
        carb_improved = test_carbs > current_carbs
        fat_improved = test_fats > current_fats
        protein_improved = test_protein < current_protein  # Lower = better
        
        nutrient_improvement = carb_improved or fat_improved or protein_improved
        fitness_improved = test_fitness < best_fitness
        
        accept = False
        accept_reason = ""
        
        # Acceptance logic
        if fitness_improved:
            # Hard acceptance: fitness lebih baik
            accept = True
            accept_reason = "FITNESS IMPROVED"
        elif nutrient_improvement and random.random() < 0.3:  # 30% soft acceptance
            # Soft acceptance: nutrient improvement tapi fitness mungkin turun
            accept = True
            accept_reason = "SOFT ACCEPT (nutrient improved)"
        
        if accept:
            best_solution = test_solution
            best_fitness = test_fitness
            improvements += 1
            no_improve_count = 0
            
            replacements.append({
                'iteration': iteration,
                'slot': slot_name,
                'old_food': current_food_name,
                'new_food': new_food_name,
                'reason': selection_reason,
                'carb_change': test_carbs - current_carbs,
                'fat_change': test_fats - current_fats,
                'protein_change': test_protein - current_protein
            })
            
            if verbose:
                print(f"[ITER {iteration}] ✓ IMPROVED - {slot_name} ({selection_reason})")
                print(f"  {current_food_name} → {new_food_name}")
                print(f"  Fitness: {best_fitness:.2f} | Carbs: {test_carbs:+.0f}g | Fats: {test_fats:+.0f}g | Protein: {test_protein:+.0f}g")
                print(f"  Reason: {accept_reason}")
        else:
            no_improve_count += 1
            if verbose:
                fitness_change = ((test_fitness - best_fitness) / best_fitness * 100) if best_fitness > 0 else 0
                print(f"[ITER {iteration}] ✗ No accept (tried {new_food_name}, fitness {fitness_change:+.1f}%, no nutrient gain)")
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"LOCAL SEARCH COMPLETE")
        print(f"{'='*70}")
        print(f"Iterations: {iteration} (stopped: no_improve_count={no_improve_count}/{max_no_improve})")
        print(f"Total improvements: {improvements}")
        print(f"Final fitness: {best_fitness:.2f}")
        
        if improvements > 0:
            print(f"\n✓ Improvements Found: {len(replacements)}")
            total_carb_change = sum(r['carb_change'] for r in replacements)
            total_fat_change = sum(r['fat_change'] for r in replacements)
            total_protein_change = sum(r['protein_change'] for r in replacements)
            
            print(f"  Total Carbs: {total_carb_change:+.1f}g")
            print(f"  Total Fats: {total_fat_change:+.1f}g")
            print(f"  Total Protein: {total_protein_change:+.1f}g")
        else:
            print(f"\n✗ No improvements found")
        
        print(f"{'='*70}\n")
    
    return best_solution


# ═════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def display_solution(solution: pd.DataFrame, guidelines: Optional[Dict] = None):
    """
    Display 10-item meal plan secara readable dengan slot labels
    
    Args:
        solution: DataFrame 10 items (chromosome)
        guidelines: Optional, untuk display constraint values
    """
    print("\n📋 MEAL PLAN (10-ITEM CHROMOSOME):")
    print("─" * 70)
    
    meal_order = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for meal_name in meal_order:
        indices = MEAL_INDICES[meal_name]
        print(f"\n{meal_name.upper()}:")
        
        slot_types = ['main', 'side', 'drink'] if meal_name != 'snack' else ['item']
        
        for i, idx in enumerate(indices):
            if idx < len(solution):
                food_row = solution.iloc[idx]
                slot_type = slot_types[i] if i < len(slot_types) else 'item'
                food_name = food_row.get('food_name', 'Unknown')
                energy = food_row.get('energy_kcal', 0)
                
                print(f"  • {slot_type.capitalize()}: {food_name} ({energy:.0f} kcal)")
    
    # Display total nutrition
    print("\n" + "─" * 70)
    total_nutrition = calculate_total_nutrition(solution)
    print(f"📊 TOTAL NUTRITION:")
    
    # Show key nutrients
    key_nutrients = ['energy_kcal', 'protein_g', 'carbohydrate_g', 'fat_g', 'fiber_g']
    for nutrient in key_nutrients:
        if nutrient in total_nutrition:
            value = total_nutrition[nutrient]
            unit = 'kcal' if 'energy' in nutrient else 'g'
            print(f"   {nutrient.replace('_', ' ').title()}: {value:.1f} {unit}")


def _calculate_nutrition_score(food_item: pd.Series) -> float:
    """
    Hitung nutrition score untuk food item
    
    Score = (0.6 * protein) + (0.3 * energy/100) - (0.1 * fat)
    
    Tujuan: Prioritas protein, energy, minimal fat
    
    Args:
        food_item: pd.Series dengan kolom energy_kcal, protein_g, fat_g
    
    Returns:
        float: Score (higher is better)
    """
    protein = food_item.get('protein_g', 0) or 0
    energy = food_item.get('energy_kcal', 0) or 0
    fat = food_item.get('fat_g', 0) or 0
    
    # Score: prioritas protein > energy > minimize fat
    score = (0.6 * protein) + (0.3 * energy / 100) - (0.1 * fat)
    
    return float(score)


def _apply_quality_filter(filtered: pd.DataFrame, expected_label: str) -> pd.DataFrame:
    """
    Apply STRICT quality filter untuk setiap food category
    Tujuan: Hindari junk food, makanan tidak realistis, dan items dengan nutrisi buruk
    
    Main Course: VERY STRICT (nutrisi balanced)
    Side Dish: STRICT (ada nutrisi, bukan lemak murni)
    Drink: MODERATE (not too calorie-dense)
    Snack: MODERATE (reasonable portions)
    
    Args:
        filtered: DataFrame yang sudah filter by label
        expected_label: Label untuk slot (e.g., 'Main Course')
    
    Returns:
        Filtered DataFrame dengan quality constraints
    
    JUNK FOOD KEYWORDS yang di-exclude:
    ['candy', 'chocolate', 'dessert', 'cake', 'cookie', 'syrup', 'donut',
     'candy bar', 'confection', 'sweet', 'sauce-fat', 'oil-pure']
    """
    if len(filtered) == 0:
        return filtered
    
    expected_lower = expected_label.strip().lower()
    
    # JUNK FOOD BLACKLIST - exclude dari semua kategori
    junk_keywords = ['candy', 'chocolate', 'dessert', 'cake', 'cookie', 'syrup', 
                     'donut', 'confection', 'sweet candy', 'caramel', 'fudge',
                     'pie', 'ice cream', 'pudding', 'mousse', 'brownie']
    junk_pattern = '|'.join(junk_keywords)
    
    # Remove junk food
    if 'food_name' in filtered.columns:
        filtered = cast(pd.DataFrame, filtered[
            ~filtered['food_name'].str.lower().str.contains(junk_pattern, na=False)
        ])
    
    # ────────────────────────────────────────────────────────────────────
    # MAIN COURSE: VERY STRICT - harus ada balanced nutrients
    # ────────────────────────────────────────────────────────────────────
    if expected_lower == 'main course':
        # Main Course HARUS:
        # - Energy 200-400 kcal (realistic portion @ 100g)
        # - Protein >= 12g (adequate protein content)
        # - Fat > 2g AND Fat < 40g (not fat-only, not too fatty)
        # - NOT pure oil/fat items
        filtered = cast(pd.DataFrame, filtered[
            (filtered['energy_kcal'] >= 200) &
            (filtered['energy_kcal'] <= 400) &
            (filtered['protein_g'] >= 12) &
            (filtered['fat_g'] >= 2) &
            (filtered['fat_g'] <= 40)
        ])
    
    # ────────────────────────────────────────────────────────────────────
    # SIDE DISH: STRICT - harus ada nutrisi, bukan hanya lemak/gula
    # ────────────────────────────────────────────────────────────────────
    elif expected_lower == 'side dish':
        # Side HARUS:
        # - Protein >= 3g (ada nutrisi, bukan empty calorie)
        # - NOT pure fat/oil (fat <= 50% of energy)
        # - NOT pure sugar
        filtered = cast(pd.DataFrame, filtered[
            (filtered['protein_g'] >= 3)
        ])
        
        # Exclude pure fat items (fat memberikan 9 kcal/g)
        # Jika fat > energy/9 * 0.7 = mostly fat → exclude
        if 'fat_g' in filtered.columns and 'energy_kcal' in filtered.columns:
            filtered = cast(pd.DataFrame, filtered[
                filtered['fat_g'] <= (filtered['energy_kcal'] / 9 * 0.7)
            ])
    
    # ────────────────────────────────────────────────────────────────────
    # DRINK: MODERATE - hindari meal replacement yang terlalu calorie-dense
    # ────────────────────────────────────────────────────────────────────
    elif expected_lower == 'drink':
        # Drink:
        # - Energy 0-200 kcal @ 100g (beverage realistic range)
        # - Exclude "meal replacement" yang sudah terlalu nutrient-dense
        if 'food_name' in filtered.columns:
            filtered = cast(pd.DataFrame, filtered[
                ~filtered['food_name'].str.lower().str.contains('meal replacement|nutritional shake', na=False)
            ])
        
        # Energy limit untuk drink
        filtered = cast(pd.DataFrame, filtered[
            filtered['energy_kcal'] <= 200
        ])
    
    # ────────────────────────────────────────────────────────────────────
    # SNACK: MODERATE - reasonable size, tidak murni junk
    # ────────────────────────────────────────────────────────────────────
    elif expected_lower == 'snack':
        # Snack:
        # - Energy 50-250 kcal (reasonable snack size)
        # - Protein >= 1g (biar ada minimal nutrisi)
        filtered = cast(pd.DataFrame, filtered[
            (filtered['energy_kcal'] >= 50) &
            (filtered['energy_kcal'] <= 250) &
            (filtered['protein_g'] >= 1)
        ])
    
    return filtered


def generate_meal_options(
    food_df: pd.DataFrame,
    top_solutions: List[pd.DataFrame],
    max_options_per_slot: int = 3,
    food_preferences: Optional[List[str]] = None
) -> Dict[str, List[pd.Series]]:
    """
    Generate 2-3 opsi menu per slot yang beragam dan tidak duplikat.
    
    Strategy SEDERHANA:
    1. Kumpulkan items dari top_solutions untuk setiap slot → basis utama
    2. Tambah variasi dari dataset dengan filtering konsumsi label
    3. Hilangkan duplikat per slot (by food_name)
    4. Hindari duplikasi global (across slots) dengan tracking used_foods
    5. Shuffle ringan untuk variasi
    6. Ambil 3 opsi pertama
    
    Args:
        food_df: DataFrame semua food items
        top_solutions: List of top 10 meal plans dari GA
        max_options_per_slot: Jumlah pilihan per slot (default 3)
        food_preferences: List of preferred cuisines (e.g., ['Asian', 'Western'])
    
    Returns:
        Dict[slot_name: [option1, option2, option3], ...]
    
    Example:
        best_sol, top_sols = run_ga(food_df, guidelines)
        options = generate_meal_options(food_df, top_sols, max_options_per_slot=3)
    """
    
    slot_options = {slot: [] for slot in SLOT_NAMES}
    used_foods = set()  # Track makanan yang sudah dipakai (hindari duplikasi global)
    
    # Prepare cuisine preferences
    if food_preferences and len(food_preferences) > 0:
        allowed_cuisine = food_preferences + ['Generic']
        allowed_cuisine = list(set(allowed_cuisine))
    else:
        allowed_cuisine = None
    
    # ════════════════════════════════════════════════════════════════════════
    # LOOP SETIAP SLOT
    # ════════════════════════════════════════════════════════════════════════
    for slot_idx in range(CHROMOSOME_SIZE):
        slot_name = SLOT_NAMES[slot_idx]
        expected_label = SLOT_LABEL_MAP[slot_idx]
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 1: Kumpulkan items dari top_solutions
        # ────────────────────────────────────────────────────────────────────
        candidates = []
        
        for solution in top_solutions:
            if slot_idx < len(solution):
                item = solution.iloc[slot_idx]
                candidates.append(item)
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 2: Tambah variasi dari dataset
        # ────────────────────────────────────────────────────────────────────
        dataset_items = cast(pd.DataFrame, food_df[
            food_df['consumption_label'].str.strip().str.lower() == expected_label.lower()
        ])
        
        # ════════════════════════════════════════════════════════════════════
        # QUALITY FILTER - Ensure dataset items meet quality standards
        # ════════════════════════════════════════════════════════════════════
        dataset_items = cast(pd.DataFrame, _apply_quality_filter(dataset_items, expected_label))
        
        # Filter by cuisine jika ada preference
        if allowed_cuisine and 'cuisine' in dataset_items.columns:
            dataset_items = dataset_items[dataset_items['cuisine'].isin(allowed_cuisine)]
        
        # Sample max 20 items dari dataset untuk variasi
        if len(dataset_items) > 20:
            dataset_items = dataset_items.sample(n=20, random_state=None)
        
        # Gabungkan candidates + dataset items (convert to Series list)
        for idx, row in dataset_items.iterrows():
            candidates.append(row)  # row is already a pd.Series
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 3: Hilangkan duplikat per slot (by food_name)
        # ────────────────────────────────────────────────────────────────────
        unique_dict = {}
        for item in candidates:
            # Safe extraction dari Series
            item_name = item.get('food_name', '') if isinstance(item, pd.Series) else getattr(item, 'food_name', '')
            if item_name and item_name not in unique_dict:
                unique_dict[item_name] = item
        
        candidates = list(unique_dict.values())
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 4: Hindari duplikasi global (dengan exception untuk Drinks)
        # ────────────────────────────────────────────────────────────────────
        # LOGIC: Strict untuk Main Course/Side Dish, tapi RELAX untuk Drink/Snack
        # Alasan: Realistis bahwa user bisa minum hal yang sama di berbagai waktu,
        #         tapi unlikely makan exact same main course di multiple slots
        # ────────────────────────────────────────────────────────────────────
        filtered_candidates = []
        is_drink_or_snack = expected_label.lower() in ['drink', 'snack']
        
        for item in candidates:
            # Safe extraction dari Series
            item_name = item.get('food_name', '') if isinstance(item, pd.Series) else getattr(item, 'food_name', '')
            
            # Untuk Drink/Snack: RELAX global dedup (allow reuse)
            # Untuk Main Course/Side Dish: STRICT global dedup (no reuse)
            if item_name:
                if is_drink_or_snack or item_name not in used_foods:
                    filtered_candidates.append(item)
        
        candidates = filtered_candidates
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 5: Shuffle ringan untuk variasi
        # ────────────────────────────────────────────────────────────────────
        random.shuffle(candidates)
        
        # ────────────────────────────────────────────────────────────────────
        # STEP 6: Ambil 3 opsi pertama
        # ────────────────────────────────────────────────────────────────────
        final_options = candidates[:max_options_per_slot]
        
        # Ensure semua adalah pd.Series untuk konsistensi
        final_options_series = []
        for opt in final_options:
            if isinstance(opt, pd.Series):
                opt_series = opt
            else:
                opt_series = pd.Series(opt)
            
            final_options_series.append(opt_series)
            
            # Track makanan yang dipakai HANYA untuk Main Course/Side Dish
            # Drink/Snack: DON'T track (allow reuse untuk realism)
            if not is_drink_or_snack:
                item_name = opt_series.get('food_name', '')
                if item_name:
                    used_foods.add(item_name)
        
        slot_options[slot_name] = final_options_series
    
    return slot_options


def display_meal_options(slot_options: Dict[str, List[pd.Series]]):
    """
    Display 3 pilihan menu per slot dengan format readable
    
    Args:
        slot_options: Dict dari generate_meal_options()
                     {slot_name: [item1, item2, item3], ...}
                     Example: 'breakfast_main', 'breakfast_side', 'breakfast_drink',
                              'lunch_main', 'lunch_side', 'lunch_drink',
                              'dinner_main', 'dinner_side', 'dinner_drink', 'snack'
    
    Example output:
        🌅 BREAKFAST
        ├─ Main Course (3 options - click one):
        │  1. Nasi Putih (180 kcal | 3.6g protein)
        │  2. Roti Tawar (250 kcal | 8.0g protein)
        │  3. Bubur Ayam (200 kcal | 5.0g protein)
        ├─ Side Dish (3 options - click one):
        │  1. Telur Rebus...
        ...
    """
    print("\n" + "="*70)
    print("✨ 3 PILIHAN MENU PER SLOT ✨")
    print("="*70)
    
    # Meal groupings for display organization
    meal_structure = {
        'breakfast': {
            'emoji': '🌅',
            'slots': ['breakfast_main', 'breakfast_side', 'breakfast_drink'],
            'slot_labels': {
                'breakfast_main': 'Main Course',
                'breakfast_side': 'Side Dish',
                'breakfast_drink': 'Beverage'
            }
        },
        'lunch': {
            'emoji': '☀️',
            'slots': ['lunch_main', 'lunch_side', 'lunch_drink'],
            'slot_labels': {
                'lunch_main': 'Main Course',
                'lunch_side': 'Side Dish',
                'lunch_drink': 'Beverage'
            }
        },
        'dinner': {
            'emoji': '🌙',
            'slots': ['dinner_main', 'dinner_side', 'dinner_drink'],
            'slot_labels': {
                'dinner_main': 'Main Course',
                'dinner_side': 'Side Dish',
                'dinner_drink': 'Beverage'
            }
        },
        'snack': {
            'emoji': '🍪',
            'slots': ['snack'],
            'slot_labels': {
                'snack': 'Snack Option'
            }
        }
    }
    
    for meal_name, meal_info in meal_structure.items():
        meal_emoji = meal_info['emoji']
        print(f"\n{meal_emoji} {meal_name.upper()}")
        print("─" * 70)
        
        for slot_idx, slot_name in enumerate(meal_info['slots']):
            slot_label = meal_info['slot_labels'].get(slot_name, slot_name)
            items = slot_options.get(slot_name, [])
            
            # Prefix for tree-like display
            is_last_slot = (slot_idx == len(meal_info['slots']) - 1)
            prefix = "└─" if is_last_slot else "├─"
            item_prefix_start = "   " if is_last_slot else "│  "
            
            print(f"{prefix} {slot_label} ({len(items)} options):")
            
            if not items:
                print(f"{item_prefix_start}   (No options available)")
                continue
            
            for opt_idx, item in enumerate(items, 1):
                food_name = item.get('food_name', 'Unknown')
                energy = item.get('energy_kcal', 0)
                protein = item.get('protein_g', 0)
                
                print(f"{item_prefix_start}   {opt_idx}. {food_name}")
                print(f"{item_prefix_start}      Energy: {energy:.0f} kcal | Protein: {protein:.1f}g")
                
                # Optional: show more nutrients
                carbs = item.get('carbohydrate_g', 0)
                fat = item.get('fat_g', 0)
                if carbs > 0 or fat > 0:
                    print(f"{item_prefix_start}      Carbs: {carbs:.1f}g | Fat: {fat:.1f}g")
    
    print("\n" + "="*70 + "\n")



def display_fitness_details(solution: pd.DataFrame, guidelines: Dict, tdee: Optional[float] = None):
    """
    Display fitness score breakdown (penalty per nutrient dengan weights)
    Gunakan weighted calculation sama seperti di fitness() function
    Handle HARD vs SOFT constraints properly
    
    Args:
        solution: DataFrame meal plan
        guidelines: Dict constraints (dengan 'hard' dan 'soft' keys jika tersedia)
        tdee: Target daily energy expenditure (opsional)
    """
    total_nutrition = calculate_total_nutrition(solution)
    total_penalty = fitness(solution, guidelines, tdee=tdee)
    
    print("\n⚖️  FITNESS BREAKDOWN:")
    print("─" * 70)
    
    # ════════════════════════════════════════════════════════════════════════
    # DETECT GUIDELINE STRUCTURE (HARD/SOFT atau LAMA)
    # ════════════════════════════════════════════════════════════════════════
    has_hard_soft = 'hard' in guidelines and 'soft' in guidelines
    
    if has_hard_soft:
        hard_constraints = guidelines['hard']
        soft_constraints = guidelines['soft']
    else:
        # Backward compatibility
        hard_constraints = {}
        soft_constraints = guidelines
    
    nutrient_penalties = {}
    violation_severity = {}  # Track HARD vs SOFT
    
    # ════════════════════════════════════════════════════════════════════════
    # HARD CONSTRAINTS CHECK (dengan multiplier 10-15x)
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in hard_constraints.items():
        if constraint.get('constraint_type') == 'unlimited':
            continue
        if nutrient_name not in total_nutrition and nutrient_name != 'energy_kcal':
            continue
        
        # Skip energy (di-handle terpisah)
        if nutrient_name == 'energy_kcal':
            continue
        
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition.get(nutrient_name, 0)
        
        # Get nutrient weight (sama seperti di fitness())
        weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
        
        penalty = 0
        status = "✓ OK"
        
        if value < min_val:
            # HARD: Kurang dari minimum dengan weight * 10
            penalty = (min_val - value) * weight * 10
            status = f"🔴 LOW (need {min_val - value:.1f} more) [HARD]"
            violation_severity[nutrient_name] = 'HARD-UNDER'
        elif value > max_val:
            # HARD: Lebih dari maximum dengan weight * 15
            penalty = (value - max_val) * weight * 15
            status = f"🔴 HIGH (excess {value - max_val:.1f}) [HARD]"
            violation_severity[nutrient_name] = 'HARD-OVER'
        
        nutrient_penalties[nutrient_name] = penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # SOFT CONSTRAINTS CHECK (dengan multiplier 1x)
    # ════════════════════════════════════════════════════════════════════════
    for nutrient_name, constraint in soft_constraints.items():
        if constraint.get('constraint_type') == 'unlimited':
            continue
        if nutrient_name not in total_nutrition and nutrient_name != 'energy_kcal':
            continue
        
        # Skip energy (di-handle terpisah)
        if nutrient_name == 'energy_kcal':
            continue
        
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        value = total_nutrition.get(nutrient_name, 0)
        
        # Get nutrient weight (sama seperti di fitness())
        weight = NUTRIENT_WEIGHTS.get(nutrient_name, 1.0)
        
        penalty = 0
        status = "✓ OK"
        
        if value < min_val:
            # SOFT: Kurang dari minimum dengan weight * 1
            penalty = (min_val - value) * weight
            status = f"🟡 LOW (need {min_val - value:.1f} more) [SOFT]"
            violation_severity[nutrient_name] = 'SOFT-UNDER'
        elif value > max_val:
            # SOFT: Lebih dari maximum dengan weight * 1
            penalty = (value - max_val) * weight
            status = f"🟡 HIGH (excess {value - max_val:.1f}) [SOFT]"
            violation_severity[nutrient_name] = 'SOFT-OVER'
        
        nutrient_penalties[nutrient_name] = penalty
    
    # ════════════════════════════════════════════════════════════════════════
    # ENERGY CONSTRAINT CHECK (HARD - CRITICAL)
    # ════════════════════════════════════════════════════════════════════════
    if tdee and tdee > 0:
        current_energy = total_nutrition.get('energy_kcal', 0)
        min_energy = 0.8 * tdee
        max_energy = 1.2 * tdee
        
        energy_penalty = 0
        energy_status = "✓ OK"
        
        if current_energy < min_energy:
            energy_penalty = (min_energy - current_energy) * 20
            energy_status = f"🔴 UNDER (need {min_energy - current_energy:.0f} more kcal) [HARD-ENERGY]"
            violation_severity['energy_kcal'] = 'HARD-ENERGY-UNDER'
        elif current_energy > max_energy:
            energy_penalty = (current_energy - max_energy) * 15
            energy_status = f"🔴 OVER (excess {current_energy - max_energy:.0f} kcal) [HARD-ENERGY]"
            violation_severity['energy_kcal'] = 'HARD-ENERGY-OVER'
        
        nutrient_penalties['energy_kcal'] = energy_penalty
    
    # Show all violations sorted by severity (HARD first, then SOFT)
    violations = [(n, p) for n, p in nutrient_penalties.items() if p > 0]
    violations.sort(key=lambda x: (-10000 if 'HARD' in violation_severity.get(x[0], '') else -1000, -x[1]))
    
    if violations:
        print(f"Violations found:\n")
        for nutrient, penalty in violations:
            severity = violation_severity.get(nutrient, 'UNKNOWN')
            multiplier = 15 if 'OVER' in severity and 'HARD' in severity else \
                        10 if 'UNDER' in severity and 'HARD' in severity else \
                        20 if 'ENERGY-UNDER' in severity else \
                        15 if 'ENERGY-OVER' in severity else 1
            print(f"   {nutrient:20} ({severity:18}): penalty = {penalty:8.2f}")
    else:
        print(f"   ✅ No violations! All constraints satisfied")
    
    print(f"\n   Total Penalty Score: {total_penalty:.2f}")


# ═════════════════════════════════════════════════════════════════════════════
# 7. CALCULATE PORTION SIZES - Hitung gram dinamis berdasarkan target energi
# ═════════════════════════════════════════════════════════════════════════════

def calculate_portion_sizes_dynamic(
    selected_df: pd.DataFrame,
    TDEE: float,
    guidelines: Optional[Dict] = None
) -> pd.DataFrame:
    """
    IMPROVED Portion Sizing dengan MACRONUTRIENT PRIORITIZATION & COMPLETE NUTRIENT SCALING
    
    Algoritma v4 - FIXED NUTRIENT RECALCULATION:
        1. Meal distribution: Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
        2. Identify ALL nutrient columns (macro + micro)
        3. Calculate totals @ 100g (ALL nutrients)
        4. Calculate deficit (carb & fat vs target) - TASK 3
        5. Deficit-aware weight: CARBS 40% + ENERGY 40% + FAT 15% + PROTEIN 5% - TASK 2
        6. Add protein portion limiting (max 150g untuk protein >20g/100g) - TASK 4
        7. Label adjustment: Snack 0.3x, Drink 0.5x, Side 0.8x, Main 1.0x
        8. Normalize weights per meal
        9. Distribute energy per meal
        10. Calculate gram dengan protein limiting
        11. Clamp realistic
        12. Renormalize setelah clamp untuk match target
        13. SCALE ALL NUTRIENTS (ALL columns) dengan portion - TASK 1
        14. Validate hasil akhir - TASK 6
    
    Tujuan:
        - TASK 1: Semua nutrient (macro+micro) ter-scale dengan benar
        - TASK 2: Carbs prioritized (40% weight + 1.5x boost)
        - TASK 3: Deficit-aware boost untuk carb/fat
        - TASK 4: Protein portion limiting
        - TASK 5: Meal normalisasi tetap correct
        - TASK 6: Validation setelah scaling
        - Tidak ada nutrient yang jadi 0 secara tidak wajar
        - Protein controlled (5% weight + portion limiting)
    
    Args:
        selected_df: DataFrame 10 selected meal items (index 0-9)
        TDEE: Total daily energy expenditure (kcal)
        guidelines: Optional dict dari NutritionService
    
    Returns:
        DataFrame dengan kolom: gram, final_* untuk SEMUA nutrient
    """
    
    # Meal distribution ratios
    meal_ratio = {
        'breakfast': 0.25,
        'lunch': 0.35,
        'dinner': 0.30,
        'snack': 0.10
    }
    
    # Mapping slot index ke meal type
    slot_to_meal = {
        0: 'breakfast', 1: 'breakfast', 2: 'breakfast',
        3: 'lunch', 4: 'lunch', 5: 'lunch',
        6: 'dinner', 7: 'dinner', 8: 'dinner',
        9: 'snack'
    }
    
    # Gram constraints realistic - TASK 4: Protein portion limiting
    gram_constraints = {
        'Main Course': (100, 300),
        'Side Dish': (50, 150),
        'Drink': (150, 300),
        'Snack': (30, 100)
    }
    
    # Label adjustment factors
    label_adjustments = {
        'Main Course': 1.0,
        'Side Dish': 0.8,
        'Drink': 0.5,
        'Snack': 0.3
    }
    
    # Extract guideline targets
    guidelines_flat = {}
    if guidelines:
        if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
            guidelines_flat = {**guidelines['hard'], **guidelines['soft']}
        else:
            guidelines_flat = guidelines
    
    target_protein_min = guidelines_flat.get('protein_g', {}).get('min', 60)
    target_protein_max = guidelines_flat.get('protein_g', {}).get('max', 120)
    target_fat_min = guidelines_flat.get('fat_g', {}).get('min', 50)
    target_fat_max = guidelines_flat.get('fat_g', {}).get('max', 100)
    target_carb_min = guidelines_flat.get('carbohydrate_g', {}).get('min', 250)
    target_carb_max = guidelines_flat.get('carbohydrate_g', {}).get('max', 350)
    
    # Copy dataframe
    result_df = selected_df.copy()
    result_df['gram'] = 0.0
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 1: IDENTIFY ALL NUTRIENT COLUMNS TO SCALE
    # Loop through all columns and identify nutrients (numeric, not metadata)
    # ════════════════════════════════════════════════════════════════════════
    nutrient_cols = []
    exclude_cols = {'fdc_id', 'food_name', 'food_group', 'consumption_label', 'cuisine_label', 'gram', 'index'}
    
    for col in result_df.columns:
        if col not in exclude_cols:
            try:
                if result_df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                    nutrient_cols.append(col)
            except:
                pass
    
    # Create final_* columns for ALL nutrients (TASK 1)
    for nutrient in nutrient_cols:
        result_df[f'final_{nutrient}'] = 0.0
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 2-3: Calculate totals @ 100g ALL NUTRIENTS (TASK 1)
    # ════════════════════════════════════════════════════════════════════════
    total_energy = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carb = 0.0
    
    for idx in range(len(result_df)):
        item = result_df.iloc[idx]
        total_energy += (item.get('energy_kcal', 0) or 0)
        total_protein += (item.get('protein_g', 0) or 0)
        total_fat += (item.get('fat_g', 0) or 0)
        total_carb += (item.get('carbohydrate_g', 0) or 0)
    
    # Prevent division by zero
    if total_energy <= 0: total_energy = 1
    if total_protein <= 0: total_protein = 1
    if total_fat <= 0: total_fat = 1
    if total_carb <= 0: total_carb = 1
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 3: Calculate deficit (kekurangan vs target) - CARBS & FAT PRIORITY
    # ════════════════════════════════════════════════════════════════════════
    carb_deficit = max(0, target_carb_min - total_carb)
    fat_deficit = max(0, target_fat_min - total_fat)
    protein_deficit = max(0, target_protein_min - total_protein)
    
    # Boost factors (TASK 3) - Macronutrient prioritization
    carb_boost = 1.5 if carb_deficit > 0 else 0.8  # STRONG boost if carbs low
    fat_boost = 1.3 if fat_deficit > 0 else 0.8    # MEDIUM boost if fats low
    protein_boost = 0.6                             # WEAK (avoid excess)
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 2: WEIGHT DISTRIBUTION - MACRONUTRIENT PRIORITIZATION
    # STEP 4: Calculate weights with NEW distribution: E:40%, C:40%, F:15%, P:5%
    # ════════════════════════════════════════════════════════════════════════
    
    weights_per_meal = {meal: [] for meal in meal_ratio.keys()}
    
    for idx in range(len(result_df)):
        item = result_df.iloc[idx]
        
        energy = (item.get('energy_kcal', 0) or 0)
        protein = (item.get('protein_g', 0) or 0)
        fat = (item.get('fat_g', 0) or 0)
        carb = (item.get('carbohydrate_g', 0) or 0)
        
        # TASK 2: NEW Weight distribution (Energy:40%, Carb:40%, Fat:15%, Protein:5%)
        weight_raw = (
            0.40 * (energy / total_energy) +
            0.40 * (carb / total_carb) * carb_boost +
            0.15 * (fat / total_fat) * fat_boost +
            0.05 * (protein / total_protein) * protein_boost
        )
        
        # Label adjustment
        label = item.get('consumption_label', 'Main Course')
        if isinstance(label, str):
            label = label.strip()
        
        adjustment = label_adjustments.get(label, 1.0)
        weight_adjusted = weight_raw * adjustment
        
        # Store untuk normalisasi per meal (TASK 5)
        meal_type = slot_to_meal.get(idx, 'snack')
        weights_per_meal[meal_type].append((idx, weight_adjusted, label, energy))
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 4: PROTEIN PORTION LIMITING
    # If protein per 100g > 20, max portion = 150g
    # If protein per 100g > 10, max portion = 200g
    # ════════════════════════════════════════════════════════════════════════
    protein_portion_limits = {}
    for idx in range(len(result_df)):
        item = result_df.iloc[idx]
        protein_per_100g = item.get('protein_g', 0) or 0
        label = item.get('consumption_label', 'Main Course')
        
        # Default constraint from label
        min_g, max_g = gram_constraints.get(label, (50, 150))
        
        # TASK 4: Apply protein-based limiting
        if protein_per_100g > 20:
            max_g = min(max_g, 150)  # Very protein-high: limit to 150g
        elif protein_per_100g > 10:
            max_g = min(max_g, 200)  # Protein-high: limit to 200g
        
        protein_portion_limits[idx] = (min_g, max_g)
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 5: MEAL NORMALIZATION & DISTRIBUTION
    # STEP 5-12: Normalize per meal, distribute energy, calc gram, clamp, renormalize
    # ════════════════════════════════════════════════════════════════════════
    
    for meal_type, ratio in meal_ratio.items():
        # TASK 5: Target energy untuk meal ini
        target_meal_energy = TDEE * ratio
        
        # Get items untuk meal ini
        meal_items = weights_per_meal[meal_type]
        if not meal_items:
            continue
        
        # Normalize weights per meal
        total_weight_meal = sum(w for _, w, _, _ in meal_items)
        if total_weight_meal <= 0:
            total_weight_meal = 1
        
        normalized_weights = [(w / total_weight_meal) for _, w, _, _ in meal_items]
        
        # First pass: calculate grams
        grams_first_pass = []
        meal_energy_first = 0
        
        for (idx, weight_adj, label, energy), norm_weight in zip(meal_items, normalized_weights):
            # Distribute energy per meal
            target_energy_item = norm_weight * target_meal_energy
            
            # Calculate gram
            energy_per_100g = energy or 1
            gram = (target_energy_item / energy_per_100g) * 100
            
            # Clamp realistic with TASK 4 protein limiting
            min_g, max_g = protein_portion_limits.get(idx, (50, 150))
            gram_clamped = np.clip(gram, min_g, max_g)
            
            grams_first_pass.append((idx, gram_clamped, energy_per_100g))
            meal_energy_first += energy_per_100g * gram_clamped / 100
        
        # Renormalize setelah clamp untuk match target meal energy
        if meal_energy_first > 0:
            scale = target_meal_energy / meal_energy_first
        else:
            scale = 1.0
        
        for idx, gram_clamped, energy_per_100g in grams_first_pass:
            gram_final = gram_clamped * scale
            result_df.at[idx, 'gram'] = round(gram_final, 1)
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 1 (CRITICAL): SCALE ALL NUTRIENTS based on portion
    # This is the key fix - ensure EVERY nutrient is scaled, not just macro
    # ════════════════════════════════════════════════════════════════════════
    
    for idx in range(len(result_df)):
        gram = result_df.at[idx, 'gram']
        actual_item = selected_df.iloc[idx]
        
        # Scale EVERY nutrient column (TASK 1)
        for nutrient in nutrient_cols:
            if nutrient in actual_item.index:
                value_per_100g = actual_item.get(nutrient, 0) or 0
                final_value = value_per_100g * gram / 100
                result_df.at[idx, f'final_{nutrient}'] = round(final_value, 2)
    
    # ════════════════════════════════════════════════════════════════════════
    # HARD CONSTRAINTS: Energy rescale to match TDEE
    # ════════════════════════════════════════════════════════════════════════
    total_energy_after = result_df['final_energy_kcal'].sum()
    
    if total_energy_after > 0 and TDEE > 0:
        energy_scale = TDEE / total_energy_after
        
        # Allow 0.6x to 1.4x scaling (reasonable range)
        if 0.6 <= energy_scale <= 1.4:
            result_df['gram'] *= energy_scale
            
            # RE-SCALE ALL NUTRIENTS with new grams (TASK 1 - critical!)
            for idx in range(len(result_df)):
                gram = result_df.at[idx, 'gram']
                actual_item = selected_df.iloc[idx]
                
                for nutrient in nutrient_cols:
                    if nutrient in actual_item.index:
                        value_per_100g = actual_item.get(nutrient, 0) or 0
                        final_value = value_per_100g * gram / 100
                        result_df.at[idx, f'final_{nutrient}'] = round(final_value, 2)
    
    # ════════════════════════════════════════════════════════════════════════
    # TASK 6: VALIDATION - Ensure scaling didn't cause anomalies
    # ════════════════════════════════════════════════════════════════════════
    
    # Check for zero nutrients that shouldn't be zero
    for idx in range(len(result_df)):
        for nutrient in nutrient_cols:
            final_col = f'final_{nutrient}'
            final_val = result_df.at[idx, final_col]
            original_val = selected_df.at[idx, nutrient] if nutrient in selected_df.columns else 0
            
            # If original had value but final is zero, something went wrong
            if original_val > 0 and final_val == 0 and result_df.at[idx, 'gram'] > 0:
                # This is anomaly - set to 0 intentionally if gram was 0, otherwise recalculate
                gram = result_df.at[idx, 'gram']
                if gram > 0:
                    recalc_val = original_val * gram / 100
                    result_df.at[idx, final_col] = round(recalc_val, 2)
    
    return result_df



def display_portion_summary_dynamic(portion_df: pd.DataFrame, guidelines: Dict, TDEE: float):
    """
    Display portion sizing hasil dengan detail per meal (v3 - SOPHISTICATED)
    
    Algorithm yang ditampilkan:
    1. Meal distribution: Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
    2. Calculate totals @ 100g
    3. Calculate deficit (kekurangan vs target)
    4. Deficit-aware weight: boost nutrients yang kurang
    5. Label adjustment: Snack 0.3x, Drink 0.5x, Side 0.8x, Main 1.0x
    6. Normalize per meal
    7. Distribute energy per meal
    8. Clamp realistic
    9. Renormalize setelah clamp untuk match target
    10. Final nutrition summary
    
    Args:
        portion_df: DataFrame hasil calculate_portion_sizes_dynamic()
        guidelines: Dict dengan constraint min/max per nutrient
        TDEE: Total daily energy expenditure (untuk reference)
    """
    print("\n" + "="*70)
    print("STEP 9: PORTION SIZING - MEAL-BASED + DEFICIT-AWARE (v3)")
    print("="*70)
    
    # FIX: Flatten guidelines if it has {'hard': {...}, 'soft': {...}} structure (for display)
    guidelines_flat_for_display = {}
    if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
        guidelines_flat_for_display = {**guidelines['hard'], **guidelines['soft']}
    else:
        guidelines_flat_for_display = guidelines
    
    print(f"\n📐 SOPHISTICATED ALGORITHM:")
    print(f"  1. Meal distribution: Breakfast 25% | Lunch 35% | Dinner 30% | Snack 10% of TDEE")
    print(f"  2. Totals @ 100g: Energy {portion_df['energy_kcal'].sum():.0f}kcal | Protein {portion_df['protein_g'].sum():.1f}g | Fat {portion_df['fat_g'].sum():.1f}g | Carb {portion_df['carbohydrate_g'].sum():.1f}g")
    print(f"  3. Calculate deficit vs targets (Protein>{guidelines_flat_for_display.get('protein_g', {}).get('min', 60)}, Fat>{guidelines_flat_for_display.get('fat_g', {}).get('min', 50)}, Carb>{guidelines_flat_for_display.get('carbohydrate_g', {}).get('min', 250)})")
    print(f"  4. Weight = 40% energy + 30% protein(×boost) + 20% fat(×boost) + 10% carb(×boost)")
    print(f"  5. Label adjustment: Main 1.0x | Side 0.8x | Drink 0.5x | Snack 0.3x")
    print(f"  6. Normalize weights per meal")
    print(f"  7. Distribute energy: Target_meal = TDEE × meal_ratio")
    print(f"  8. Clamp: Main 100-300g | Side 50-150g | Drink 150-300g | Snack 30-100g")
    print(f"  9. Renormalize setelah clamp untuk match target_meal_energy")
    
    print(f"\n📊 YOUR PERSONALIZED MEAL PORTIONS:")
    print(f"─" * 70)
    
    # Display by meal type
    meal_display_order = [
        ('breakfast', '🌅 BREAKFAST', [0, 1, 2]),
        ('lunch', '☀️ LUNCH', [3, 4, 5]),
        ('dinner', '🌙 DINNER', [6, 7, 8]),
        ('snack', '🍪 SNACK', [9])
    ]
    
    meal_totals = {}
    
    for meal_name, meal_emoji, indices in meal_display_order:
        print(f"\n{meal_emoji}")
        print(f"─" * 70)
        
        meal_energy = 0
        meal_protein = 0
        meal_items = []
        
        for idx in indices:
            if idx >= len(portion_df):
                continue
            
            item = portion_df.iloc[idx]
            
            food_name = item.get('food_name', f'Item {idx}')
            gram = item.get('gram', 0)
            final_energy = item.get('final_energy_kcal', 0)
            final_protein = item.get('final_protein_g', 0)
            final_carbs = item.get('final_carbohydrate_g', 0)
            final_fat = item.get('final_fat_g', 0)
            label = item.get('consumption_label', 'Unknown')
            
            meal_items.append({
                'name': food_name,
                'gram': gram,
                'label': label,
                'energy': final_energy,
                'protein': final_protein,
                'carbs': final_carbs,
                'fat': final_fat
            })
            
            meal_energy += final_energy
            meal_protein += final_protein
            
            # Display item
            print(f"  • {food_name[:40]}")
            print(f"    Label: {label} | Portion: {gram:.0f}g")
            print(f"    Energy: {final_energy:.0f} kcal | Protein: {final_protein:.1f}g | Carbs: {final_carbs:.1f}g | Fat: {final_fat:.1f}g")
        
        meal_totals[meal_name] = {
            'energy': meal_energy,
            'protein': meal_protein,
            'items': meal_items
        }
    
    # Display daily totals
    print(f"\n" + "="*70)
    print(f"📈 DAILY NUTRITION SUMMARY:")
    print(f"─" * 70)
    
    total_energy = portion_df['final_energy_kcal'].sum()
    total_protein = portion_df['final_protein_g'].sum()
    total_carbs = portion_df['final_carbohydrate_g'].sum()
    total_fat = portion_df['final_fat_g'].sum()
    total_fiber = portion_df['final_fiber_g'].sum()
    total_sodium = portion_df['final_sodium_mg'].sum()
    
    for meal_name, meal_emoji, _ in meal_display_order:
        if meal_name in meal_totals:
            energy = meal_totals[meal_name]['energy']
            protein = meal_totals[meal_name]['protein']
            print(f"  {meal_emoji} {meal_name.upper():10}: {energy:6.0f} kcal | {protein:5.1f}g protein")
    
    print(f"\n  {'─'*66}")
    print(f"  {'TOTAL':10}: {total_energy:6.0f} kcal | {total_protein:5.1f}g protein")
    print(f"              {total_carbs:6.1f}g carbs | {total_fat:6.1f}g fat | {total_sodium:6.0f}mg sodium")
    
    # Show compliance vs target
    print(f"\n📋 COMPLIANCE vs GUIDELINES (ALL NUTRIENTS):")
    print(f"─" * 120)
    
    # FIX: Flatten guidelines if it has {'hard': {...}, 'soft': {...}} structure
    guidelines_flat = {}
    if isinstance(guidelines, dict) and 'hard' in guidelines and 'soft' in guidelines:
        guidelines_flat = {**guidelines['hard'], **guidelines['soft']}
    else:
        guidelines_flat = guidelines
    
    # Define unit mapping untuk common nutrients
    unit_map = {
        'energy_kcal': 'kcal',
        'protein_g': 'g',
        'carbohydrate_g': 'g',
        'fat_g': 'g',
        'fiber_g': 'g',
        'sodium_mg': 'mg',
        'potassium_mg': 'mg',
        'cholesterol_mg': 'mg',
        'calcium_mg': 'mg',
        'iron_mg': 'mg',
        'magnesium_mg': 'mg',
        'phosphorus_mg': 'mg',
        'zinc_mg': 'mg',
        'vitamin_a_mcg': 'mcg',
        'vitamin_b1_mg': 'mg',
        'vitamin_b2_mg': 'mg',
        'vitamin_b3_mg': 'mg',
        'vitamin_b5_mg': 'mg',
        'vitamin_b6_mg': 'mg',
        'vitamin_b12_mcg': 'mcg',
        'vitamin_c_mg': 'mg',
        'vitamin_d_mcg': 'mcg',
        'vitamin_e_mg': 'mg',
        'vitamin_k_mcg': 'mcg',
        'folate_mcg': 'mcg',
    }
    
    # Format nutrient name untuk display
    def format_nutrient_label(nutrient_col: str) -> str:
        """Convert nutrient_col ke readable label"""
        # Contoh: energy_kcal → Energy, protein_g → Protein
        name = nutrient_col.replace('_', ' ').replace('kcal', '').replace('mg', '').replace('g', '').replace('mcg', '').strip()
        # Capitalize each word
        return ' '.join(word.capitalize() for word in name.split())
    
    # Get actual values dari portion_df
    final_nutrition = {}
    for nutrient in guidelines_flat.keys():
        # Try to get from portion_df columns like 'final_protein_g'
        final_col = f'final_{nutrient}'
        if final_col in portion_df.columns:
            final_nutrition[nutrient] = portion_df[final_col].sum()
        else:
            # Fallback: calculate dari food data
            final_nutrition[nutrient] = 0
    
    # Print table header
    print(f"{'Nutrient':<30} {'Actual':>12} {'Min':>12} {'Max':>12} {'Status':>12} {'Details':>20}")
    print(f"─" * 120)
    
    compliant_count = 0
    total_checks = 0
    
    # Loop ALL nutrients dari guidelines (TIDAK HANYA 5!)
    for nutrient_col, constraint in sorted(guidelines_flat.items()):
        # Skip unlimited constraints
        if constraint.get('constraint_type') == 'unlimited':
            continue
        
        # Get actual value
        actual_val = final_nutrition.get(nutrient_col, 0)
        
        # Skip jika tidak ada value
        if actual_val == 0 and nutrient_col not in final_nutrition:
            continue
        
        min_val = constraint.get('min', 0)
        max_val = constraint.get('max', float('inf'))
        
        # Get unit dari mapping atau dari constraint
        unit = unit_map.get(nutrient_col, constraint.get('unit', ''))
        
        # Format nutrient label
        label = format_nutrient_label(nutrient_col)
        
        total_checks += 1
        
        # Determine status dengan indikator yang jelas
        if min_val <= actual_val <= max_val:
            status = "✅ OK"
            details = "Within range"
            compliant_count += 1
        elif actual_val < min_val:
            deficit = min_val - actual_val
            status = "🔴 LOW"
            details = f"Need +{deficit:.1f} {unit}"
        else:
            excess = actual_val - max_val
            status = "🟡 HIGH"
            details = f"Excess {excess:.1f} {unit}"
        
        # Display row
        print(f"{label:<30} {actual_val:>12.1f} {min_val:>12.1f} {max_val:>12.1f} {status:>12} {details:>20}")
    
    # Summary compliance
    print(f"─" * 120)
    
    compliance_pct = (compliant_count / total_checks * 100) if total_checks > 0 else 0
    compliance_bar = "█" * int(compliance_pct / 5) + "░" * (20 - int(compliance_pct / 5))
    
    print(f"\n  {'Total nutrients checked':<30} {total_checks:>10}")
    print(f"  {'Compliant nutrients':<30} {compliant_count:>10}")
    print(f"  {'Compliance Rate':<30} {compliance_pct:>6.1f}% [{compliance_bar}]")
    print(f"  {'Status':<30} {'✅ GOOD' if compliance_pct >= 80 else '⚠️  FAIR' if compliance_pct >= 50 else '❌ POOR'}")
    print(f"  {'🎯 Target TDEE':<30} {TDEE:>10.0f} kcal")
    print(f"  {'📊 Actual Energy':<30} {total_energy:>10.0f} kcal")
    print(f"  {'📈 Difference':<30} {abs(total_energy - TDEE):>+10.0f} kcal")
    
    print(f"\n" + "="*70 + "\n")
