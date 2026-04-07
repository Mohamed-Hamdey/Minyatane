import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------
NUM_CARS = 50
RECORDS_PER_CAR = 100

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
# GENERATE DATA
# -----------------------------
data = []

start_date = datetime(2023, 1, 1)

for car_id in range(1, NUM_CARS + 1):

    # random starting km
    current_km = random.randint(50000, 150000)

    for _ in range(RECORDS_PER_CAR):

        part = random.choice(PARTS)

        # simulate last change km
        max_life = PARTS_LIFETIME_KM[part]
        km_diff = random.randint(0, int(max_life * 1.5))

        last_change_km = current_km - km_diff

        # simulate time difference
        days_diff = random.randint(1, 400)
        last_change_date = start_date - timedelta(days=days_diff)
        current_date = start_date

        # label generation
        if km_diff > max_life:
            needs_change = 1
        else:
            needs_change = 0

        data.append({
            "car_id": car_id,
            "part": part,
            "current_km": current_km,
            "last_change_km": last_change_km,
            "km_diff": km_diff,
            "days_diff": days_diff,
            "needs_change": needs_change
        })

# -----------------------------
# CREATE DATAFRAME
# -----------------------------
df = pd.DataFrame(data)

# shuffle dataset
df = df.sample(frac=1).reset_index(drop=True)

# -----------------------------
# SAVE DATA
# -----------------------------
df.to_csv("car_maintenance_dataset.csv", index=False)

print("✅ Dataset generated successfully!")
print(df.head())