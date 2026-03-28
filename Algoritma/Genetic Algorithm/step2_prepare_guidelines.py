import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

GUIDELINE_PATH = os.path.join(PROJECT_ROOT, "Data Raw", "guideline.csv")


def load_guideline():

    df = pd.read_csv(GUIDELINE_PATH)

    # ubah koma menjadi titik
    df["min"] = df["min"].astype(str).str.replace(",", ".", regex=False)
    df["max"] = df["max"].astype(str).str.replace(",", ".", regex=False)

    # ubah ke numeric
    df["min"] = pd.to_numeric(df["min"], errors="coerce")
    df["max"] = pd.to_numeric(df["max"], errors="coerce")

    return df


def build_constraint_dict(df):

    constraints = {}

    for _, row in df.iterrows():

        disease = row["disease"]
        nutrient = row["nutrient"]

        if disease not in constraints:
            constraints[disease] = {}

        constraints[disease][nutrient] = {
            "min": row["min"],
            "max": row["max"]
        }

    return constraints


if __name__ == "__main__":

    guideline_df = load_guideline()

    print("Clean guideline sample:")
    print(guideline_df.head())

    constraint_dict = build_constraint_dict(guideline_df)

    print("\nExample constraint for DM2:")
    print(constraint_dict.get("dm2"))