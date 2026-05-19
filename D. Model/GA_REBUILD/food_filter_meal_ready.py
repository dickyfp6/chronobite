# =====================================================
# MEAL-READY FOOD FILTER
# =====================================================
# Filter non-meal foods (dried, powder, spice, etc)
# WITHOUT modifying original dataset
# Create filtered copy for GA/Local Search optimization
# =====================================================

import pandas as pd
from pathlib import Path
from typing import Optional, Union


def filter_meal_ready_foods(
    input_csv: Union[str, pd.DataFrame],
    output_csv: Optional[str] = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Filter meal-ready foods from dataset
    
    TASK 1: Keyword-based filter (removes non-meal items)
    TASK 2: Energy filter (removes low-energy items)
    TASK 3: Preserve important categories (no category removal)
    TASK 4: Validate results
    
    Args:
        input_csv: Path to input dataset CSV or pandas DataFrame
        output_csv: Path to save filtered dataset (optional)
        verbose: Print detailed filtering info
        
    Returns:
        Filtered pandas DataFrame
    """
    
    # Load data
    print("\n" + "="*70)
    print("MEAL-READY FOOD FILTER")
    print("="*70)
    
    # Handle both DataFrame and CSV path input
    if isinstance(input_csv, pd.DataFrame):
        food_df = input_csv.copy()
        print(f"\n[LOAD] Using provided DataFrame")
    else:
        print(f"\n[LOAD] Loading dataset from: {input_csv}")
        food_df = pd.read_csv(input_csv)
    
    initial_count = len(food_df)
    
    if verbose:
        print(f"[OK] Loaded {initial_count} items")
    
    # =================================================================
    # TASK 1: KEYWORD-BASED FILTER
    # =================================================================
    if verbose:
        print("\n" + "="*70)
        print("TASK 1: KEYWORD-BASED FILTER - Remove Non-Meal Foods")
        print("="*70)
    
    invalid_keywords = [
        'dried', 'freeze-dried', 'freeze dried',
        'powder', 'powdered',
        'spice', 'spices', 'spiced',
        'herb', 'herbs', 'herbal',
        'seasoning', 'seasonings',
        'extract', 'extracts',
        'flavoring', 'flavorings', 'flavouring',
        'yeast',
        'bran'
    ]
    
    before_keyword = len(food_df)
    
    # Apply keyword filter - filter out items containing ANY of the invalid keywords
    mask = pd.Series([False] * len(food_df), index=food_df.index)
    for keyword in invalid_keywords:
        mask = mask | food_df['food_name'].str.lower().str.contains(keyword, na=False, regex=False)
    
    food_df = food_df[~mask]
    
    removed_keyword = before_keyword - len(food_df)
    
    if verbose:
        print(f"Items before keyword filter: {before_keyword}")
        print(f"Items removed (non-meal foods): {removed_keyword}")
        print(f"Items remaining: {len(food_df)}")
    
    # =================================================================
    # TASK 2: ENERGY FILTER - Remove Low-Energy Items
    # =================================================================
    if verbose:
        print("\n" + "="*70)
        print("TASK 2: ENERGY FILTER - Remove Low-Energy Items")
        print("="*70)
    
    before_energy = len(food_df)
    
    # Filter energy >= 50 kcal to remove lightweight items (bumbu, garnish, dll)
    food_df = food_df[food_df['energy_kcal'] >= 50]
    
    removed_energy = before_energy - len(food_df)
    
    if verbose:
        print(f"Items before energy filter: {before_energy}")
        print(f"Items removed (energy < 50 kcal): {removed_energy}")
        print(f"Items remaining: {len(food_df)}")
    
    # =================================================================
    # TASK 3: VALIDATE - Don't Remove by Category
    # =================================================================
    if verbose:
        print("\n" + "="*70)
        print("TASK 3: VALIDATE - Preserving Important Categories")
        print("="*70)
    
    # Verify important categories still exist
    important_categories = [
        'Vegetables and Vegetable Products',
        'Fruits and Fruit Juices',
        'Dairy and Egg Products'
    ]
    
    for cat in important_categories:
        if 'food_group' in food_df.columns:
            count = (food_df['food_group'] == cat).sum()
            if count > 0 and verbose:
                print(f"[OK] {cat}: {count} items retained")
    
    if verbose:
        print("[OK] Filtering based on food form (not category)")
    
    # =================================================================
    # TASK 4: VALIDATION - Filter Results Summary
    # =================================================================
    if verbose:
        print("\n" + "="*70)
        print("TASK 4: VALIDATION - Filter Results Summary")
        print("="*70)
    
    final_count = len(food_df)
    total_removed = removed_keyword + removed_energy
    
    if verbose:
        print(f"\n[SUMMARY] FILTERING SUMMARY:")
        print(f"  Initial dataset size: {initial_count}")
        print(f"  Removed (non-meal): {removed_keyword}")
        print(f"  Removed (low energy): {removed_energy}")
        print(f"  Total removed: {total_removed}")
        print(f"  Final dataset size: {final_count}")
        print(f"  Retention rate: {(final_count/initial_count)*100:.1f}%")
    
    # Verify no remaining junk items
    junk_keywords = ['spearmint', 'dried peppers', 'freeze-dried', 'powder', 'spice']
    remaining_junk_count = 0
    
    if verbose:
        print(f"\n  Junk item verification:")
    
    for keyword in junk_keywords:
        count = food_df['food_name'].str.lower().str.contains(keyword, na=False).sum()
        if count > 0:
            if verbose:
                print(f"  [WARN] WARNING: Still contains '{keyword}': {count} items")
            remaining_junk_count += count
        else:
            if verbose:
                print(f"  [OK] Removed all '{keyword}' items")
    
    if remaining_junk_count == 0:
        if verbose:
            print(f"\n[PASS] VALIDATION PASSED - No junk items remaining")
    else:
        if verbose:
            print(f"\n[WARN] WARNING: {remaining_junk_count} junk items still remain")
    
    # Verify dataset size is acceptable
    if final_count >= 2000:
        if verbose:
            print(f"[PASS] Dataset size acceptable (>= 2000 items): {final_count}")
    else:
        if verbose:
            print(f"[WARN] WARNING: Dataset size below 2000 items: {final_count}")
    
    # =================================================================
    # SAVE FILTERED DATASET (optional)
    # =================================================================
    if output_csv:
        print(f"\n[SAVE] Saving filtered dataset to: {output_csv}")
        food_df.to_csv(output_csv, index=False)
        print(f"[OK] Filtered dataset saved ({len(food_df)} items)")
    
    if verbose:
        print("\n" + "="*70)
        print("[DONE] MEAL-READY FILTER COMPLETE")
        print("="*70)
    
    return food_df


# =================================================================
# MAIN - Run filter if executed directly
# =================================================================
if __name__ == "__main__":
    # Paths
    repo_root = Path(__file__).parent.parent.parent
    input_file = repo_root / "A. Data/Data Processed/05_final_dataset.csv"
    output_file = Path(__file__).parent / "05_final_dataset_filtered.csv"
    
    # Run filter
    filtered_df = filter_meal_ready_foods(
        input_csv=str(input_file),
        output_csv=str(output_file),
        verbose=True
    )
    
    print(f"\n[OK] Output file saved: {output_file}")
    print(f"[OK] Ready to use with GA/Local Search")
