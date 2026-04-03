# import random
# import json

# from step4_prepare_food_candidates import build_food_pool
# from Trash.Preprocess.step5_generate_initial_population import generate_population
# from Trash.Preprocess.step6_fitness_function import fitness_function


# # ======================================================
# # PARAMETERS
# # ======================================================

# POPULATION_SIZE = 120
# GENERATIONS = 100

# CROSSOVER_RATE = 0.9
# MUTATION_RATE = 0.25
# ELITISM = 4

# LOCAL_SEARCH_ITER = 600


# # ======================================================
# # CHROMOSOME DISTANCE
# # ======================================================

# def chromosome_distance(c1, c2):

#     diff = 0

#     for a,b in zip(c1,c2):
#         if a != b:
#             diff += 1

#     return diff


# # ======================================================
# # TOURNAMENT SELECTION
# # ======================================================

# def tournament_selection(population, fitnesses, k=3):

#     idxs = random.sample(range(len(population)), k)

#     best = idxs[0]

#     for i in idxs:
#         if fitnesses[i] > fitnesses[best]:
#             best = i

#     return population[best].copy()


# # ======================================================
# # CROSSOVER
# # ======================================================

# def crossover(parent1, parent2):

#     if random.random() > CROSSOVER_RATE:
#         return parent1.copy(), parent2.copy()

#     point = random.randint(1, len(parent1)-2)

#     child1 = parent1[:point] + parent2[point:]
#     child2 = parent2[:point] + parent1[point:]

#     return child1, child2


# # ======================================================
# # MUTATION
# # ======================================================

# def mutate(chromosome, food_pool):

#     if random.random() > MUTATION_RATE:
#         return chromosome

#     idx = random.randint(0, len(chromosome)-1)

#     food_type = idx % 4

#     if food_type == 0:
#         pool = food_pool["main_course"]
#     elif food_type == 1:
#         pool = food_pool["side_dish"]
#     elif food_type == 2:
#         pool = food_pool["drink"]
#     else:
#         pool = food_pool["dessert_snack"]

#     new_food = int(pool.sample(1).iloc[0]["fdc_id"])

#     while new_food == chromosome[idx]:
#         new_food = int(pool.sample(1).iloc[0]["fdc_id"])

#     chromosome[idx] = new_food

#     return chromosome


# # ======================================================
# # LOCAL SEARCH
# # ======================================================

# def local_search(chromosome, food_pool):

#     best = chromosome.copy()
#     best_fit, _ = fitness_function(best)

#     for _ in range(LOCAL_SEARCH_ITER):

#         candidate = best.copy()

#         changes = random.randint(1,3)

#         for _ in range(changes):

#             idx = random.randint(0, len(candidate)-1)

#             food_type = idx % 4

#             if food_type == 0:
#                 pool = food_pool["main_course"]
#             elif food_type == 1:
#                 pool = food_pool["side_dish"]
#             elif food_type == 2:
#                 pool = food_pool["drink"]
#             else:
#                 pool = food_pool["dessert_snack"]

#             new_food = int(pool.sample(1).iloc[0]["fdc_id"])

#             while new_food == candidate[idx]:
#                 new_food = int(pool.sample(1).iloc[0]["fdc_id"])

#             candidate[idx] = new_food

#         fit,_ = fitness_function(candidate)

#         if fit > best_fit:
#             best = candidate
#             best_fit = fit

#     return best, best_fit


# # ======================================================
# # GENETIC ALGORITHM
# # ======================================================

# def run_ga_ls():

#     food_pool, preference = build_food_pool()

#     population = generate_population(food_pool, POPULATION_SIZE)

#     best_history = []

#     global_best = None
#     global_best_fit = -1


#     for gen in range(GENERATIONS):

#         fitnesses = []

#         for chrom in population:
#             fit,_ = fitness_function(chrom)
#             fitnesses.append(fit)

#         ranked = sorted(
#             zip(population, fitnesses),
#             key=lambda x: x[1],
#             reverse=True
#         )

#         population = [x[0] for x in ranked]
#         fitnesses = [x[1] for x in ranked]

#         best_fit = fitnesses[0]

#         best_history.append(best_fit)

#         print(f"Generation {gen} Best fitness: {round(best_fit,4)}")

#         if best_fit > global_best_fit:
#             global_best = population[0].copy()
#             global_best_fit = best_fit

#         new_population = population[:ELITISM]

#         while len(new_population) < POPULATION_SIZE:

#             p1 = tournament_selection(population, fitnesses)
#             p2 = tournament_selection(population, fitnesses)

#             c1, c2 = crossover(p1, p2)

#             c1 = mutate(c1, food_pool)
#             c2 = mutate(c2, food_pool)

#             new_population.append(c1)

#             if len(new_population) < POPULATION_SIZE:
#                 new_population.append(c2)

#         population = new_population


#     # ======================================================
#     # LOCAL SEARCH
#     # ======================================================

#     print("\n===== BEFORE LOCAL SEARCH =====")
#     print("Fitness:", global_best_fit)

#     option1, improved_fit = local_search(global_best, food_pool)

#     print("\n===== AFTER LOCAL SEARCH =====")
#     print("Fitness:", improved_fit)


#     # ======================================================
#     # FIND SECOND SOLUTION
#     # ======================================================

#     fitnesses = []

#     for chrom in population:
#         fit,_ = fitness_function(chrom)
#         fitnesses.append(fit)

#     ranked = sorted(
#         zip(population, fitnesses),
#         key=lambda x: x[1],
#         reverse=True
#     )

#     option2 = None

#     for chrom,fit in ranked:

#         if chromosome_distance(option1, chrom) >= 4:
#             option2 = chrom.copy()
#             break


#     if option2 is None:

#         option2 = option1.copy()

#         for _ in range(3):

#             idx = random.randint(0, len(option2)-1)

#             food_type = idx % 4

#             if food_type == 0:
#                 pool = food_pool["main_course"]
#             elif food_type == 1:
#                 pool = food_pool["side_dish"]
#             elif food_type == 2:
#                 pool = food_pool["drink"]
#             else:
#                 pool = food_pool["dessert_snack"]

#             new_food = int(pool.sample(1).iloc[0]["fdc_id"])

#             option2[idx] = new_food


#     fit2,_ = fitness_function(option2)


#     # ======================================================
#     # SAVE RESULT
#     # ======================================================

#     result = {
#         "option1": option1,
#         "option2": option2,
#         "fitness_option1": improved_fit,
#         "fitness_option2": fit2
#     }

#     with open("Algoritma/Genetic Algorithm/File/best_menu_result.json","w") as f:
#         json.dump(result,f)

#     print("\nBest solutions saved to best_menu_result.json")

#     return option1, option2, improved_fit, best_history


# # ======================================================
# # TEST
# # ======================================================

# if __name__ == "__main__":

#     option1, option2, fitness, history = run_ga_ls()

#     print("\n===== FINAL FITNESS =====")
#     print(fitness)