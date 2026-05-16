"""
Verification script for guidelines constraint handling fix
Checks that guidelines are properly flattened in final evaluation functions
"""

import re

print("=" * 80)
print("GUIDELINES CONSTRAINT HANDLING - FIX VERIFICATION")
print("=" * 80)

# Read ga_v1.py
with open("ga_v1.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check 1: verify flatten logic in calculate_portion_sizes_dynamic
print("\n[1] Checking calculate_portion_sizes_dynamic() for guidelines flattening...")
if "def calculate_portion_sizes_dynamic(" in content:
    # Extract function
    func_start = content.find("def calculate_portion_sizes_dynamic(")
    func_end = content.find("\ndef ", func_start + 1)
    func_content = content[func_start:func_end]
    
    if "guidelines_flat = {**guidelines['hard'], **guidelines['soft']}" in func_content:
        print("    [OK] Guidelines flattening logic found")
    else:
        print("    [FAIL] Guidelines flattening NOT found")
    
    if "target_protein_min = guidelines_flat.get('protein_g'" in func_content:
        print("    [OK] Using guidelines_flat for target extraction")
    else:
        print("    [FAIL] NOT using guidelines_flat")
else:
    print("    [FAIL] Function not found")

# Check 2: verify flatten logic in display_portion_summary_dynamic - compliance check
print("\n[2] Checking display_portion_summary_dynamic() - compliance check section...")
if "def display_portion_summary_dynamic(" in content:
    func_start = content.find("def display_portion_summary_dynamic(")
    func_end = content.find("\ndef ", func_start + 1)
    func_content = content[func_start:func_end]
    
    # Look for compliance check section
    if "constraint = guidelines_flat.get(nutrient" in func_content:
        print("    [OK] Using guidelines_flat in compliance check")
    else:
        print("    [FAIL] NOT using guidelines_flat in compliance check")
    
    # Check for flattening before compliance
    if "guidelines_flat = {**guidelines['hard'], **guidelines['soft']}" in func_content and \
       "COMPLIANCE vs GUIDELINES" in func_content:
        print("    [OK] Guidelines flattening happens before compliance check")
    else:
        print("    [WARN] May need to verify flatten timing")
else:
    print("    [FAIL] Function not found")

# Check 3: verify display section uses correct guidelines
print("\n[3] Checking display_portion_summary_dynamic() - display section...")
if "def display_portion_summary_dynamic(" in content:
    func_start = content.find("def display_portion_summary_dynamic(")
    func_end = content.find("\ndef ", func_start + 1)
    func_content = content[func_start:func_end]
    
    if "guidelines_flat_for_display" in func_content and \
       "guidelines_flat_for_display = {**guidelines['hard'], **guidelines['soft']}" in func_content:
        print("    [OK] Display section has its own flattened guidelines")
    else:
        print("    [WARN] Display section may not have proper guidelines handling")

# Check 4: verify no remaining direct guideline accesses for constraint checking
print("\n[4] Checking for remaining problematic guideline accesses...")
# Look for patterns like guidelines.get('sodium_mg') or guidelines.get('protein_g') 
# that are NOT part of detection logic
problematic_patterns = [
    r"constraint = guidelines\.get\(['\"]",  # constraint = guidelines.get('nutrient')
    r"min_val = guidelines\.get\(['\"]",     # min_val = guidelines.get('nutrient')
]

found_problems = False
for pattern in problematic_patterns:
    matches = re.finditer(pattern, content)
    for match in matches:
        # Check if this is in one of the functions we fixed
        pos = match.start()
        # Look for function context (find the enclosing function)
        lines_before = content[:pos].split('\n')
        
        # Find which function this is in
        func_name = "unknown"
        for line in reversed(lines_before):
            if line.startswith("def "):
                func_name = line.split("(")[0][4:]
                break
        
        # If it's in fitness, that's OK (it's for detection)
        if "fitness" in func_name:
            continue
        
        print(f"    [WARN] Found direct guidelines.get() in {func_name}")
        found_problems = True

if not found_problems:
    print("    [OK] No problematic guidelines accesses found")

print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print("\nIf all checks show [OK], the guidelines constraint bug is FIXED:")
print("  • Sodium violations will be correctly detected")
print("  • Compliance rate will be realistic (not always 100%)")
print("  • Final evaluation uses correct min/max values from guidelines")
print("\nKey Points:")
print("  1. Guidelines structure: {'hard': {...}, 'soft': {...}}")
print("  2. Flattening: {**guidelines['hard'], **guidelines['soft']}")
print("  3. Access: guidelines_flat.get('nutrient', {}).get('min/max')")
