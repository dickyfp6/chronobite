import json

from step1_load_data import load_food_dataset


# ======================================================
# LOAD DATA
# ======================================================

food_df = load_food_dataset()


# ======================================================
# LOAD HASIL STEP7 (GA + LS)
# ======================================================

with open("Algoritma/Genetic Algorithm/File/best_menu_result.json", "r") as f:
    result = json.load(f)

option1 = result["option1"]
option2 = result["option2"]


# ======================================================
# AMBIL DATA MAKANAN
# ======================================================

def get_food(fid):

    row = food_df[food_df["fdc_id"] == fid]

    if row.empty:
        return None

    return row.iloc[0]


# ======================================================
# TAMPILKAN MENU
# ======================================================

def show_menu(chromosome, label):

    meals = ["Breakfast", "Lunch", "Dinner"]

    idx = 0

    print("\n==============================")
    print(f"        OPTION {label}")
    print("==============================")

    for meal in meals:

        main = get_food(chromosome[idx])
        side = get_food(chromosome[idx+1])
        drink = get_food(chromosome[idx+2])
        snack = get_food(chromosome[idx+3])

        print(f"\n{meal}")

        print("Main  :", main["food_name"])
        print("Side  :", side["food_name"])
        print("Drink :", drink["food_name"])
        print("Snack :", snack["food_name"])

        idx += 4


# ======================================================
# VALIDASI INPUT
# ======================================================

def ask_choice(text):

    while True:

        val = input(text)

        if val in ["1","2"]:
            return int(val)

        print("Input harus 1 atau 2")


# ======================================================
# GABUNGKAN PILIHAN USER
# ======================================================

def build_final_menu(opt1, opt2, b, l, d):

    final_menu = []

    choices = [
        (b,0),
        (l,4),
        (d,8)
    ]

    for choice,start in choices:

        if choice == 1:
            final_menu.extend(opt1[start:start+4])
        else:
            final_menu.extend(opt2[start:start+4])

    return final_menu


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    show_menu(option1,1)
    show_menu(option2,2)

    print("\n===== USER MENU SELECTION =====")

    b = ask_choice("Breakfast option (1/2): ")
    l = ask_choice("Lunch option (1/2): ")
    d = ask_choice("Dinner option (1/2): ")

    final_menu = build_final_menu(option1, option2, b, l, d)

    with open("Algoritma/Genetic Algorithm/File/user_selected_menu.json", "w") as f:
        json.dump(final_menu, f)

    print("\nMenu pilihan user disimpan ke user_selected_menu.json")