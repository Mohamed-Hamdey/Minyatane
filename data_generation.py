import pandas as pd
import numpy as np
import random

# -----------------------------
# CONFIG
# -----------------------------
INPUT_FILE = "car_maintenance_dataset_full.csv"
OUTPUT_FILE = "car_maintenance_dataset_expanded.csv"

NEW_RECORDS = 100000

PARTS_LIFETIME_KM = {
    "oil": 5000,
    "air_filter": 8000,
    "brake_pads": 20000,
    "battery": 45000,
    "tires": 60000,
    "spark_plugs": 30000,
    "fuel_filter": 15000
}

# NEW: time-based thresholds (days)
PARTS_LIFETIME_DAYS = {
    "oil": 90,
    "air_filter": 180,
    "brake_pads": 365,
    "battery": 720,
    "tires": 900,
    "spark_plugs": 540,
    "fuel_filter": 300
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

    # pick random car
    car_id = random.choice(df["car_id"].unique())

    part = random.choice(PARTS)

    # -----------------------------
    # REALISTIC CURRENT KM
    # -----------------------------
    current_km = int(np.random.normal(
        df["current_km"].mean(),
        df["current_km"].std()
    ))
    current_km = max(5000, current_km)

    # -----------------------------
    # KM DIFF (better distribution)
    # -----------------------------
    km_threshold = PARTS_LIFETIME_KM[part]

    # mixture distribution (normal + extreme cases)
    if random.random() < 0.8:
        km_diff = int(np.random.normal(km_threshold * 0.7, km_threshold * 0.3))
    else:
        # overdue / neglected cases
        km_diff = int(np.random.normal(km_threshold * 1.5, km_threshold * 0.5))

    km_diff = max(0, km_diff)

    last_change_km = current_km - km_diff

    # -----------------------------
    # DAYS DIFF (important fix 🔥)
    # -----------------------------
    time_threshold = PARTS_LIFETIME_DAYS[part]

    if random.random() < 0.7:
        days_diff = int(np.random.normal(time_threshold * 0.7, time_threshold * 0.4))
    else:
        days_diff = int(np.random.normal(time_threshold * 1.5, time_threshold * 0.6))

    days_diff = max(1, days_diff)

    # -----------------------------
    # SMART LABEL (km + time)
    # -----------------------------
    km_score = km_diff / km_threshold
    time_score = days_diff / time_threshold

    # weighted score (km slightly more important)
    score = 0.7 * km_score + 0.3 * time_score

    if score > 1:
        needs_change = 1
    else:
        needs_change = 0

    # -----------------------------
    # ADD REALISTIC NOISE 🔥
    # -----------------------------
    noise = random.random()

    if needs_change == 1 and noise < 0.1:
        needs_change = 0  # missed maintenance
    elif needs_change == 0 and noise < 0.1:
        needs_change = 1  # early maintenance

    # -----------------------------
    # SAVE ROW
    # -----------------------------
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
# MERGE
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