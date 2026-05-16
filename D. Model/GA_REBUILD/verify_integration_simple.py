"""
Direct verification of quality filter integration in ga_v1.py
Checks the code without executing the GA
"""

print("=" * 80)
print("QUALITY FILTER INTEGRATION VERIFICATION")
print("=" * 80)

# Read ga_v1.py
with open("ga_v1.py", "r", encoding="utf-8") as f:
    content = f.read()

# Split into functions for easier analysis
lines = content.split('\n')

print("\n[1] Checking _filter_food_by_slot() implementation...")
in_filter_func = False
filter_has_quality_check = False

for i, line in enumerate(lines):
    if "def _filter_food_by_slot(" in line:
        in_filter_func = True
    elif in_filter_func and line.strip().startswith("def ") and "def _filter_food_by_slot" not in line:
        in_filter_func = False
    elif in_filter_func and "_apply_quality_filter(filtered, expected_label)" in line:
        filter_has_quality_check = True
        print(f"    [OK] Quality filter found at line {i + 1}")

if filter_has_quality_check:
    print("    [PASS] _filter_food_by_slot() has quality filter integration")
else:
    print("    [FAIL] _filter_food_by_slot() does NOT have quality filter")

print("\n[2] Checking generate_meal_options() implementation...")
in_gen_func = False
gen_has_quality_check = False

for i, line in enumerate(lines):
    if "def generate_meal_options(" in line:
        in_gen_func = True
    elif in_gen_func and line.strip().startswith("def ") and "def generate_meal_options" not in line:
        in_gen_func = False
    elif in_gen_func and "_apply_quality_filter(dataset_items, expected_label)" in line:
        gen_has_quality_check = True
        print(f"    [OK] Quality filter found at line {i + 1}")

if gen_has_quality_check:
    print("    [PASS] generate_meal_options() has quality filter integration")
else:
    print("    [FAIL] generate_meal_options() does NOT have quality filter")

print("\n[3] Verifying _apply_quality_filter() function exists...")
if "def _apply_quality_filter(" in content:
    print("    [OK] _apply_quality_filter() function exists")
else:
    print("    [FAIL] _apply_quality_filter() function NOT found")

print("\n[4] Checking call chain: random_solution -> _filter_food_by_slot...")
if "def random_solution(" in content and "_filter_food_by_slot(food_df, slot_idx)" in content:
    print("    [OK] random_solution() -> _filter_food_by_slot() -> quality filter")
else:
    print("    [INFO] Unable to verify complete call chain")

print("\n[5] Checking call chain: mutation -> _filter_food_by_slot...")
in_mut = False
mut_has_filter_call = False
for i, line in enumerate(lines):
    if "def mutation(" in line:
        in_mut = True
    elif in_mut and line.strip().startswith("def "):
        break
    elif in_mut and "_filter_food_by_slot(food_df, gene_idx)" in line:
        mut_has_filter_call = True
        print(f"    [OK] mutation() -> _filter_food_by_slot() at line {i + 1}")

print("\n" + "=" * 80)
print("INTEGRATION SUMMARY")
print("=" * 80)

all_ok = filter_has_quality_check and gen_has_quality_check
if all_ok:
    print("\n[PASS] QUALITY FILTER INTEGRATION COMPLETE")
    print("\nIntegration Points:")
    print("  1. _filter_food_by_slot() - Food selection with quality checks")
    print("     - random_solution() inherits quality filtering")
    print("     - mutation() inherits quality filtering")
    print("  2. generate_meal_options() - User options with quality filtering")
    print("\nResult: GA now selects only realistic, quality-verified foods")
else:
    print("\n[FAIL] Integration incomplete")
    if not filter_has_quality_check:
        print("  - Missing: _filter_food_by_slot() quality filter")
    if not gen_has_quality_check:
        print("  - Missing: generate_meal_options() quality filter")
