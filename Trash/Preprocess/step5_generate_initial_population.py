import random

from step4_prepare_food_candidates import build_food_pool
from step3_user_nutrition_needs import build_user_profile


# ======================================================
# Cari nama kolom energi yang tersedia
# ======================================================

def detect_energy_column(df):

    if "energy_kcal" in df.columns:
        return "energy_kcal"

    if "Energy" in df.columns:
        return "Energy"

    return None


# ======================================================
# Filter makanan ekstrem
# ======================================================

def filter_food(df):

    df = df.copy()

    if "sodium_mg" in df.columns:
        df = df[df["sodium_mg"] <= 2000]

    energy_col = detect_energy_column(df)

    if energy_col is not None:
        df = df[df[energy_col] <= 800]

    return df


# ======================================================
# Sampling makanan mendekati target energi
# ======================================================

def sample_food_by_energy(df, target_energy, used_ids):

    candidates = df.copy()

    candidates = candidates[~candidates["fdc_id"].isin(used_ids)]

    if candidates.empty:
        candidates = df.copy()

    energy_col = detect_energy_column(candidates)

    # Jika tidak ada kolom energi → random saja
    if energy_col is None:
        row = candidates.sample(1).iloc[0]
        return int(row["fdc_id"])

    candidates["energy_diff"] = abs(candidates[energy_col] - target_energy)

    candidates = candidates.sort_values("energy_diff")

    top = candidates.head(10)

    row = top.sample(1).iloc[0]

    return int(row["fdc_id"])


# ======================================================
# Generate 1 chromosome
# ======================================================

def generate_chromosome(food_pool):

    user_profile = build_user_profile()

    energy_need = user_profile["energy_need"]

    breakfast_target = energy_need * 0.25
    lunch_target = energy_need * 0.40
    dinner_target = energy_need * 0.30

    meal_targets = [breakfast_target, lunch_target, dinner_target]

    main_pool = filter_food(food_pool["main_course"])
    side_pool = filter_food(food_pool["side_dish"])
    drink_pool = filter_food(food_pool["drink"])
    snack_pool = filter_food(food_pool["dessert_snack"])

    chromosome = []
    used_ids = set()

    for target in meal_targets:

        main = sample_food_by_energy(main_pool, target * 0.6, used_ids)
        used_ids.add(main)

        side = sample_food_by_energy(side_pool, target * 0.25, used_ids)
        used_ids.add(side)

        drink = sample_food_by_energy(drink_pool, target * 0.1, used_ids)
        used_ids.add(drink)

        snack = sample_food_by_energy(snack_pool, target * 0.15, used_ids)
        used_ids.add(snack)

        chromosome.extend([main, side, drink, snack])

    return chromosome


# ======================================================
# Generate population
# ======================================================

def generate_population(food_pool, population_size=50):

    population = []

    for _ in range(population_size):

        chromosome = generate_chromosome(food_pool)

        population.append(chromosome)

    return population


# ======================================================
# Pretty print chromosome
# ======================================================

def print_chromosome(chromosome):

    meals = ["Breakfast", "Lunch", "Dinner"]

    idx = 0

    for meal in meals:

        main = chromosome[idx]
        side = chromosome[idx + 1]
        drink = chromosome[idx + 2]
        snack = chromosome[idx + 3]

        print(f"{meal}:")
        print("  Main :", main)
        print("  Side :", side)
        print("  Drink:", drink)
        print("  Snack:", snack)
        print()

        idx += 4


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    food_pool, preference = build_food_pool()

    population = generate_population(food_pool, population_size=3)

    print("\n===== USER CUISINE =====")
    print(preference)

    print("\n===== INITIAL POPULATION SAMPLE =====")

    for i, chrom in enumerate(population):

        print(f"\nChromosome {i+1}")
        print_chromosome(chrom)