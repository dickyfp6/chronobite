"""
DEMO: Nutrient Fulfillment Display with Percentages
====================================================

Menunjukkan bagaimana output nutrient analysis terlihat dengan percentage fulfillment
"""

def calculate_fulfillment_percentage(value, min_val, max_val):
    """Calculate fulfillment percentage"""
    if min_val == 0 and max_val == float('inf'):
        return 100.0
    
    if value < min_val:
        percent = (value / min_val * 100) if min_val > 0 else 0
    elif value > max_val:
        percent = (max_val / value * 100) if value > 0 else 0
    else:
        percent = 100.0
    
    return percent


def get_status_category(percent):
    """Categorize fulfillment status"""
    if percent >= 95:
        return ("Excellent", "✨")
    elif percent >= 85:
        return ("Good", "🟢")
    elif percent >= 70:
        return ("Fair", "🟡")
    else:
        return ("Poor", "🔴")


def format_fulfillment_display(value, min_val, max_val, unit):
    """Format display string"""
    percent = calculate_fulfillment_percentage(value, min_val, max_val)
    status_text, emoji = get_status_category(percent)
    
    if max_val == float('inf'):
        display_str = f"{value:.1f} / min {min_val:.1f} {unit}"
    else:
        display_str = f"{value:.1f} ({min_val:.1f}-{max_val:.1f}) {unit}"
    
    return display_str, percent, status_text, emoji


# Sample nutrition data
nutrients = [
    ("energy_kcal", "Energy", 1800, 2000, 2300, "kcal"),
    ("carbohydrate_g", "Carbohydrate", 197, 192, 277, "g"),
    ("protein_g", "Protein", 75, 50, 120, "g"),
    ("fat_g", "Fat", 45, 50, 100, "g"),
    ("fiber_g", "Fiber", 32, 30, 38, "g"),
    ("sodium_mg", "Sodium", 1200, 0, 2300, "mg"),
    ("cholesterol_mg", "Cholesterol", 180, 0, 200, "mg"),
    ("calcium_mg", "Calcium", 900, 1000, 1200, "mg"),
    ("iron_mg", "Iron", 12, 8, 27, "mg"),
    ("vitamin_c_mg", "Vitamin C", 65, 75, 1000, "mg"),
]

print("\n" + "="*130)
print("DEMO: Nutrient Fulfillment with Percentage Analysis")
print("="*130)

print("\n📊 DETAILED NUTRIENT ANALYSIS (ALL MACRO + MICRO):")
print("─" * 130)
print(f"{'Nutrient':<30} {'Value / Target':<35} {'Fulfill %':>12} {'Status':>20} {'Category':>12}")
print("─" * 130)

compliant = 0
total_checks = 0

for col_name, label, value, min_val, max_val, unit in nutrients:
    display_str, percent, status_text, emoji = format_fulfillment_display(value, min_val, max_val, unit)
    
    total_checks += 1
    if percent >= 70 or (min_val <= value <= max_val):
        compliant += 1
    
    percent_str = f"{percent:.1f}%"
    status_display = f"{emoji} {status_text}"
    
    print(f"{label:<30} {display_str:<35} {percent_str:>12} {status_display:>20} {'':<12}")

print("─" * 130)

# Summary
print(f"\n{'Total nutrients checked':<30} {total_checks:>10}")
print(f"{'Nutrients >= 70% fulfilled':<30} {compliant:>10}")

if total_checks > 0:
    compliance_rate = (compliant / total_checks) * 100
    compliance_bar = "█" * int(compliance_rate / 5) + "░" * (20 - int(compliance_rate / 5))
    print(f"\n{'Fulfillment Rate':<30} {compliance_rate:>6.1f}% [{compliance_bar}]")
    
    if compliance_rate >= 90:
        overall_status = "🌟 EXCELLENT - Outstanding nutrition profile"
    elif compliance_rate >= 80:
        overall_status = "🟢 GOOD - Strong nutrition balance"
    elif compliance_rate >= 70:
        overall_status = "🟡 FAIR - Acceptable nutrition profile"
    else:
        overall_status = "🔴 POOR - Needs improvement"
    
    print(f"{'Overall Assessment':<30} {overall_status}")

print("\n" + "="*130)

# Explanation
print("\n[INTERPRETATION GUIDE]")
print("─" * 130)
print("✨ Excellent (>= 95%): Nutrient value is very close to target or well within range")
print("🟢 Good (85-94%):       Nutrient value meets guideline with minor variation")
print("🟡 Fair (70-84%):       Nutrient value is acceptable but slightly below/above ideal")
print("🔴 Poor (< 70%):        Nutrient value is significantly below/above target")
print("\n[PERCENTAGE CALCULATION]")
print("─" * 130)
print("For RANGE (min-max):")
print("  - If value < min: percent = (value / min) * 100")
print("  - If value in [min, max]: percent = 100%")
print("  - If value > max: percent = (max / value) * 100")
print("\nFor EXACT TARGET (min == max):")
print("  - percent = (1 - abs(value - target) / target) * 100")
print("\n" + "="*130 + "\n")
