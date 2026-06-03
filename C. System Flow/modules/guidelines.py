"""
Module untuk process dan convert guideline
"""

import sys
import os

# Add parent directory to path untuk import data_loader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import get_guideline_loader
from modules.calculations import NutritionCalculator


class GuidelineProcessor:
    """Class untuk process guideline berdasarkan kondisi user"""

    def __init__(self):
        """Initialize guideline processor"""
        self.loader = get_guideline_loader()
        self.calc = NutritionCalculator()

    def get_nutrition_guidelines(self, user_data, nutrition_results):
        """
        Get dan convert guideline nutrisi untuk user.

        Proses 2 tahap:
          Step 1 – Konversi setiap guideline per disease ke unit aktual,
                   lalu kumpulkan semua nilai per nutrient.
          Step 2 – Merge multi-disease dengan strategi most-restrictive
                   (min terbesar, max terkecil). Jika konflik (min > max),
                   fallback ke union range disertai peringatan.

        Args:
            user_data        : dict dari input_handler
            nutrition_results: dict hasil dari calculations

        Returns:
            dict: Guidelines terkonversi dengan nutrient constraints,
                  atau None jika tidak ada guideline ditemukan.
        """
        disease     = user_data['disease']
        age         = user_data['age']
        gender      = user_data['gender']
        user_params = nutrition_results['user_params']

        # Support single disease (str) maupun multiple diseases (list)
        disease_list = disease if isinstance(disease, list) else [disease]

        # ── Step 1: Kumpulkan converted values per nutrient per disease ──────
        # Struktur: {nutrient: [(min_converted, max_converted, constraint_type, basis), ...]}
        all_converted = {}
        disease_names = []

        for disease_item in disease_list:
            guideline_df = self.loader.get_guideline_by_disease(
                disease_item, age, gender
            )

            if guideline_df.empty:
                print(f"[WARN] No guideline found for disease={disease_item}, "
                      f"age={age}, gender={gender}")
                continue

            disease_names.append(disease_item)

            for _, row in guideline_df.iterrows():
                nutrient = row['nutrient']
                basis    = row['basis']

                # Konversi ke unit aktual (gram / kcal) sesuai basis & nutrient
                converted = self.calc.convert_guideline_value(
                    row['min'], row['max'], basis, user_params,
                    nutrient_name=nutrient
                )

                # Lewati hasil konversi yang tidak valid
                if converted['constraint_type'] in ('invalid', 'unknown'):
                    continue

                all_converted.setdefault(nutrient, []).append((
                    converted['min_converted'],
                    converted['max_converted'],
                    converted['constraint_type'],
                    basis
                ))

        # ── Step 2: Merge semua converted values ─────────────────────────────
        guidelines_dict = {}

        for nutrient, values in all_converted.items():
            mins   = [v[0] for v in values]
            maxes  = [v[1] for v in values]
            c_type = values[0][2]
            basis  = values[0][3]

            # Strategi most-restrictive: min terbesar & max terkecil
            merged_min = max(mins)
            merged_max = min(maxes)

            # Conflict check: jika min > max, fallback ke union range
            if merged_min > merged_max:
                union_min = min(mins)
                union_max = max(maxes)
                print(f"[WARN] Conflict on '{nutrient}': "
                      f"merged min {merged_min:.2f} > max {merged_max:.2f}. "
                      f"Falling back to union range "
                      f"{union_min:.2f} – {union_max:.2f}")
                merged_min = union_min
                merged_max = union_max

            guidelines_dict[nutrient] = {
                'min':             merged_min,
                'max':             merged_max,
                'basis':           basis,
                'constraint_type': c_type,
                'source':          'guideline'
            }

        if not guidelines_dict:
            print("[WARN] No guidelines found for any diseases")
            return None

        return {
            'disease':          ', '.join(disease_names) if disease_names else str(disease),
            'guidelines':       guidelines_dict,
            'total_guidelines': len(guidelines_dict)
        }

    def display_guidelines(self, guidelines_result, nutrition_results):
        """
        Display guideline dalam format yang readable.

        Args:
            guidelines_result: dict dari get_nutrition_guidelines()
            nutrition_results: dict hasil dari calculations
        """
        if guidelines_result is None:
            print("No guidelines available")
            return

        print("\n" + "=" * 70)
        print("KEBUTUHAN NUTRISI BERDASARKAN GUIDELINE")
        print("=" * 70)
        print(f"\nKondisi Kesehatan : {guidelines_result['disease'].upper()}")
        print(f"Jumlah Nutrient   : {guidelines_result['total_guidelines']}")
        print("\nDaftar Kebutuhan Nutrisi:")
        print("-" * 70)

        label_map = {
            'unlimited':           lambda n, c: f"{n:30} | No limit (unlimited)",
            'absolute':            lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f}",
            'partial_absolute':    lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f}",
            'tdee_based':          lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f} (dari TDEE)",
            'partial_tdee_based':  lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f} (dari TDEE)",
            'weight_based':        lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f} (dari BB)",
            'partial_weight_based':lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f} (dari BB)",
            'bbi_based':           lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f} (dari BBI)",
            'partial_bbi_based':   lambda n, c: f"{n:30} | {c['min']:10.2f} - {c['max']:10.2f} (dari BBI)",
        }

        for nutrient, constraint in guidelines_result['guidelines'].items():
            c_type   = constraint['constraint_type']
            formatter = label_map.get(c_type)
            if formatter:
                print(formatter(nutrient, constraint))
            else:
                print(f"{nutrient:30} | Invalid constraint ({c_type})")

        print("-" * 70)


def process_user_guidelines(user_data, nutrition_results):
    """
    Main function untuk process guidelines.

    Args:
        user_data        : dict dari input_handler
        nutrition_results: dict hasil dari calculations

    Returns:
        dict dengan keys:
            'processor'  – instance GuidelineProcessor
            'guidelines' – hasil get_nutrition_guidelines()
    """
    processor  = GuidelineProcessor()
    guidelines = processor.get_nutrition_guidelines(user_data, nutrition_results)
    return {
        'processor':  processor,
        'guidelines': guidelines
    }