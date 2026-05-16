def calculate_portion_sizes_dynamic_v2(
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
