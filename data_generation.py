import pandas as pd
import numpy as np
import random

# -----------------------------
# CONFIG
# -----------------------------
INPUT_FILE = "car_maintenance_dataset.csv"
OUTPUT_FILE = "car_maintenance_dataset_expanded.csv"

NEW_RECORDS = 100000  # how many new rows you want

PARTS_LIFETIME_KM = {
    "oil": 5000,
    "air_filter": 10000,
    "brake_pads": 20000,
    "battery": 40000,
    "tires": 50000,
    "spark_plugs": 30000,
    "fuel_filter": 15000
}

PARTS = list(PARTS_LIFETIME_KM.keys())

# -----------------------------
# LOAD EXISTING DATA
# -----------------------------
df = pd.read_csv(INPUT_FILE)

new_data = []

# -----------------------------
# GENERATE MORE DATA
# -----------------------------
for _ in range(NEW_RECORDS):

    # pick a random existing car
    car_id = random.choice(df["car_id"].unique())

    part = random.choice(PARTS)

    # simulate current km based on existing distribution
    current_km = int(np.random.normal(
        df["current_km"].mean(),
        df["current_km"].std()
    ))

    current_km = max(1000, current_km)

    max_life = PARTS_LIFETIME_KM[part]

    # generate km_diff with more realism
    km_diff = int(np.random.normal(max_life * 0.8, max_life * 0.5))
    km_diff = max(0, km_diff)

    last_change_km = current_km - km_diff

    days_diff = random.randint(1, 500)

    # label
    needs_change = 1 if km_diff > max_life else 0

    new_data.append({
        "car_id": car_id,
        "part": part,
        "current_km": current_km,
        "last_change_km": last_change_km,
        "km_diff": km_diff,
        "days_diff": days_diff,
        "needs_change": needs_change
    })

# -----------------------------
# MERGE DATA
# -----------------------------
new_df = pd.DataFrame(new_data)

final_df = pd.concat([df, new_df], ignore_index=True)

# shuffle
final_df = final_df.sample(frac=1).reset_index(drop=True)

# -----------------------------
# SAVE
# -----------------------------
final_df.to_csv(OUTPUT_FILE, index=False)

print("✅ Dataset expanded successfully!")
print(f"Old size: {len(df)}")
print(f"New size: {len(final_df)}")