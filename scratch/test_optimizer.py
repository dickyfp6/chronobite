import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'D. Model', 'Greedy Algorithm')))
from greedy_02_optimizer import GreedyOptimizer

def main():
    opt = GreedyOptimizer(pd.DataFrame(), {})
    
    # 273g = 649.7 kcal => ~238 kcal per 100g
    # 150g = 268.5 kcal => ~179 kcal per 100g
    # 100g = 63.0 kcal => 63 kcal per 100g
    
    main_item = {'food_name': 'Breaded Veal Cutlet', 'energy_kcal': 238.0}
    side_item = {'food_name': 'Peanut Sauce', 'energy_kcal': 179.0}
    drink_item = {'food_name': 'Chocolate Soymilk', 'energy_kcal': 63.0}
    
    min_target = 476.0
    max_target = 595.0
    target_mid = 535.5
    
    min_m, max_m = 100.0, 300.0
    min_s, max_s = 50.0, 150.0
    min_d, max_d = 100.0, 250.0
    
    COURSE_DISTRIBUTION = {
        'Main': 0.50,
        'Side': 0.30,
        'Drink': 0.20,
    }
    
    best_error = float('inf')
    best_portions = (min_m, min_s, min_d)
    
    energy_m = main_item['energy_kcal']
    energy_s = side_item['energy_kcal']
    energy_d = drink_item['energy_kcal']
    
    for m in range(int(min_m), int(max_m) + 1):
        s_upper = min(max_s, m - 1.0)
        if s_upper < min_s:
            continue
            
        d_upper = min(max_d, m - 1.0)
        if d_upper < min_d:
            continue
            
        for s in range(int(min_s), int(s_upper) + 1):
            cal_ms = (m * energy_m + s * energy_s) / 100.0
            needed_cal_d = target_mid - cal_ms
            
            ideal_d = (needed_cal_d * 100.0) / energy_d if energy_d > 0 else min_d
            d = max(min_d, min(d_upper, ideal_d))
            d = float(round(d))
            
            cal_d = (d * energy_d) / 100.0
            total_cal = cal_ms + cal_d
            
            if total_cal < min_target:
                error = min_target - total_cal
            elif total_cal > max_target:
                error = total_cal - max_target
            else:
                error = abs(total_cal - target_mid) * 0.1
            
            # Print specifically for m=150 and m=273 to see their errors
            if (m == 150 and s == 50) or (m == 273 and s == 150):
                print(f"DEBUG: m={m}, s={s}, d={d}")
                print(f"  cal_m={(m*energy_m)/100.0}, cal_s={(s*energy_s)/100.0}, cal_d={cal_d}, total={total_cal}")
                print(f"  base_error={error}")
                
            if total_cal > 0:
                cal_m = (m * energy_m) / 100.0
                cal_s = (s * energy_s) / 100.0
                perc_m = cal_m / total_cal
                perc_s = cal_s / total_cal
                perc_d = cal_d / total_cal
                
                dist_error_m = abs(perc_m - COURSE_DISTRIBUTION['Main'])
                dist_error_s = abs(perc_s - COURSE_DISTRIBUTION['Side'])
                dist_error_d = abs(perc_d - COURSE_DISTRIBUTION['Drink'])
                
                dist_penalty = (dist_error_m + dist_error_s + dist_error_d) * 500.0
                error += dist_penalty
                
                if (m == 150 and s == 50) or (m == 273 and s == 150):
                    print(f"  dist_penalty={dist_penalty}, FINAL ERROR={error}")
                    
            if error < best_error:
                best_error = error
                best_portions = (float(m), float(s), float(d))
                
    print(f"\nWINNER: m={best_portions[0]}, s={best_portions[1]}, d={best_portions[2]} with error {best_error}")

if __name__ == '__main__':
    main()
