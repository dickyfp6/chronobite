import os

path = os.path.abspath(r"D. Model/Genetic Algorithm/ga_dicky.py")
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Convert lines to strip whitespace for matching
stripped = [line.strip() for line in lines]

# Find target 1 indices (in evaluate_population_vectorized)
idx_1 = -1
for i in range(len(stripped) - 3):
    if (stripped[i] == "clamped_grams = np.clip(grams, min_grams, max_grams)" and
        stripped[i+1] == "clamped_grams = np.round(clamped_grams)" and
        stripped[i+3] == "multipliers = clamped_grams / 100.0"):
        idx_1 = i
        break

if idx_1 != -1:
    print("Found Target 1 at line", idx_1 + 1)
    replacement_1 = [
        "        clamped_grams = np.clip(grams, min_grams, max_grams)\n",
        "        clamped_grams = np.round(clamped_grams)\n",
        "\n",
        "        # Enforce portion hierarchy: Main > Side and Main > Drink for Breakfast, Lunch, Dinner\n",
        "        is_1d = clamped_grams.ndim == 1\n",
        "        if is_1d:\n",
        "            clamped_grams = clamped_grams[np.newaxis, :]\n",
        "        epsilon = 1.0\n",
        "        for m, s, d in [(0, 1, 2), (3, 4, 5), (6, 7, 8)]:\n",
        "            # 1. Adjust Side if Side >= Main\n",
        "            violation_side = clamped_grams[:, s] >= clamped_grams[:, m]\n",
        "            clamped_grams[violation_side, s] = np.maximum(min_grams[s], clamped_grams[violation_side, m] - epsilon)\n",
        "            \n",
        "            # 2. Adjust Drink if Drink >= Main\n",
        "            violation_drink = clamped_grams[:, d] >= clamped_grams[:, m]\n",
        "            clamped_grams[violation_drink, d] = np.maximum(min_grams[d], clamped_grams[violation_drink, m] - epsilon)\n",
        "            \n",
        "            # 3. Adjust Main if Main <= max(Side, Drink)\n",
        "            max_non_main = np.maximum(clamped_grams[:, s], clamped_grams[:, d])\n",
        "            violation_main = clamped_grams[:, m] <= max_non_main\n",
        "            clamped_grams[violation_main, m] = np.minimum(max_grams[m], max_non_main[violation_main] + epsilon)\n",
        "        if is_1d:\n",
        "            clamped_grams = clamped_grams[0]\n",
        "\n",
        "        multipliers = clamped_grams / 100.0\n"
    ]
    lines[idx_1:idx_1+4] = replacement_1
else:
    print("ERROR: Target 1 not found!")

# Regenerate stripped list for the second search (because indices shifted)
stripped = [line.strip() for line in lines]
idx_2 = -1
for i in range(len(stripped) - 3):
    if (stripped[i] == "clamped_grams = np.clip(grams, min_grams, max_grams)" and
        stripped[i+1] == "clamped_grams = np.round(clamped_grams)" and
        stripped[i+3] == "result['gram'] = clamped_grams"):
        idx_2 = i
        break

if idx_2 != -1:
    print("Found Target 2 at line", idx_2 + 1)
    replacement_2 = [
        "        clamped_grams = np.clip(grams, min_grams, max_grams)\n",
        "        clamped_grams = np.round(clamped_grams)\n",
        "\n",
        "        # Enforce portion hierarchy: Main > Side and Main > Drink for Breakfast, Lunch, Dinner\n",
        "        is_1d = clamped_grams.ndim == 1\n",
        "        if is_1d:\n",
        "            clamped_grams = clamped_grams[np.newaxis, :]\n",
        "        epsilon = 1.0\n",
        "        for m, s, d in [(0, 1, 2), (3, 4, 5), (6, 7, 8)]:\n",
        "            # 1. Adjust Side if Side >= Main\n",
        "            violation_side = clamped_grams[:, s] >= clamped_grams[:, m]\n",
        "            clamped_grams[violation_side, s] = np.maximum(min_grams[s], clamped_grams[violation_side, m] - epsilon)\n",
        "            \n",
        "            # 2. Adjust Drink if Drink >= Main\n",
        "            violation_drink = clamped_grams[:, d] >= clamped_grams[:, m]\n",
        "            clamped_grams[violation_drink, d] = np.maximum(min_grams[d], clamped_grams[violation_drink, m] - epsilon)\n",
        "            \n",
        "            # 3. Adjust Main if Main <= max(Side, Drink)\n",
        "            max_non_main = np.maximum(clamped_grams[:, s], clamped_grams[:, d])\n",
        "            violation_main = clamped_grams[:, m] <= max_non_main\n",
        "            clamped_grams[violation_main, m] = np.minimum(max_grams[m], max_non_main[violation_main] + epsilon)\n",
        "        if is_1d:\n",
        "            clamped_grams = clamped_grams[0]\n",
        "\n",
        "        result['gram'] = clamped_grams\n"
    ]
    lines[idx_2:idx_2+4] = replacement_2
else:
    print("ERROR: Target 2 not found!")

# Regenerate stripped list for the third search
stripped = [line.strip() for line in lines]
idx_3 = -1
for i in range(len(stripped) - 10):
    if (stripped[i] == "# Apply meal_scale ke gram items dalam meal" and
        stripped[i+1] == "for idx in meal_indices:"):
        idx_3 = i
        break

if idx_3 != -1:
    print("Found Target 3 at line", idx_3 + 1)
    
    end_idx = idx_3 + 2
    while "result_df.at[idx, f'final_{nutrient}'] = round" not in stripped[end_idx]:
        end_idx += 1
    end_idx += 1
    
    replacement_3 = [
        "        # Apply meal_scale ke gram items dalam meal\n",
        "        for idx in meal_indices:\n",
        "            scaled_gram = result_df.at[idx, 'gram'] * meal_scale\n",
        "            rounded_gram = round(scaled_gram)\n",
        "\n",
        "            # Clamp ke protein_portion_limits\n",
        "            min_g, max_g = protein_portion_limits.get(idx, (50, 150))\n",
        "            clamped_gram = max(min_g, min(max_g, rounded_gram))\n",
        "\n",
        "            result_df.at[idx, 'gram'] = float(clamped_gram)\n",
        "\n",
        "    # ENFORCE PORTION HIERARCHY (Main > Side and Main > Drink)\n",
        "    epsilon = 1.0\n",
        "    for m, s, d in [(0, 1, 2), (3, 4, 5), (6, 7, 8)]:\n",
        "        min_m, max_m = protein_portion_limits.get(m, (100, 300))\n",
        "        min_s, max_s = protein_portion_limits.get(s, (50, 150))\n",
        "        min_d, max_d = protein_portion_limits.get(d, (100, 250))\n",
        "        \n",
        "        main_g = result_df.at[m, 'gram']\n",
        "        side_g = result_df.at[s, 'gram']\n",
        "        drink_g = result_df.at[d, 'gram']\n",
        "        \n",
        "        # 1. Adjust Side if Side >= Main\n",
        "        if side_g >= main_g:\n",
        "            side_g = max(min_s, main_g - epsilon)\n",
        "            result_df.at[s, 'gram'] = float(round(side_g))\n",
        "            \n",
        "        # 2. Adjust Drink if Drink >= Main\n",
        "        if drink_g >= main_g:\n",
        "            drink_g = max(min_d, main_g - epsilon)\n",
        "            result_df.at[d, 'gram'] = float(round(drink_g))\n",
        "            \n",
        "        # 3. If Main is still <= max(Side, Drink), we must increase Main\n",
        "        main_g = result_df.at[m, 'gram']\n",
        "        side_g = result_df.at[s, 'gram']\n",
        "        drink_g = result_df.at[d, 'gram']\n",
        "        max_non_main = max(side_g, drink_g)\n",
        "        \n",
        "        if main_g <= max_non_main:\n",
        "            main_g = min(max_m, max_non_main + epsilon)\n",
        "            result_df.at[m, 'gram'] = float(round(main_g))\n",
        "\n",
        "    # Re-scale ALL NUTRIENTS untuk semua items dengan gram baru (TASK 1)\n",
        "    for idx in range(CHROMOSOME_SIZE):\n",
        "        gram = result_df.at[idx, 'gram']\n",
        "        actual_item = selected_df.iloc[idx]\n",
        "\n",
        "        for nutrient in nutrient_cols:\n",
        "            if nutrient in actual_item.index:\n",
        "                value_per_100g = actual_item.get(nutrient, 0) or 0\n",
        "                final_value = value_per_100g * gram / 100\n",
        "                result_df.at[idx, f'final_{nutrient}'] = round(final_value, 2)\n"
    ]
    
    lines[idx_3:end_idx+1] = replacement_3
else:
    print("ERROR: Target 3 not found!")

# Write content back using standard python write
with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Replacement completed and saved.")
