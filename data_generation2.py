import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------
NUM_CARS = 50
RECORDS_PER_CAR = 100
random.seed(42)
np.random.seed(42)

# Part lifetime in KM + days threshold
PARTS_CONFIG = {
    "brake_pads":       {"km": 25000, "days": 365,  "critical": True},
    "timing_chain":     {"km": 60000, "days": 730,  "critical": True},
    "belts_kit":        {"km": 40000, "days": 548,  "critical": True},
    "spark_plugs":      {"km": 30000, "days": 365,  "critical": False},
    "wire_set":         {"km": 50000, "days": 548,  "critical": False},
    "fuel_filter":      {"km": 20000, "days": 365,  "critical": False},
    "air_filter":       {"km": 15000, "days": 180,  "critical": False},
    "battery":          {"km": 50000, "days": 730,  "critical": False},
    "tire":             {"km": 40000, "days": 548,  "critical": True},
    "brake_fluid_p":    {"km": 30000, "days": 365,  "critical": True},
    "brake_fluid_r":    {"km": 30000, "days": 365,  "critical": True},
}

PARTS = list(PARTS_CONFIG.keys())

# Car profiles — simulates different real-world usage behaviors
CAR_PROFILES = {
    "heavy_use":      {"km_per_day": (150, 250), "weight": 0.25},   # long-route buses
    "normal_use":     {"km_per_day": (60, 149),  "weight": 0.45},   # typical university cars
    "light_use":      {"km_per_day": (20, 59),   "weight": 0.20},   # admin/short trips
    "irregular_use":  {"km_per_day": (5, 300),   "weight": 0.10},   # sits for weeks then spikes
}

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def assign_car_profile():
    profiles = list(CAR_PROFILES.keys())
    weights = [CAR_PROFILES[p]["weight"] for p in profiles]
    return random.choices(profiles, weights=weights, k=1)[0]

def get_km_per_day(profile):
    lo, hi = CAR_PROFILES[profile]["km_per_day"]
    if profile == "irregular_use":
        # bimodal: either very low or very high
        if random.random() < 0.5:
            return random.randint(5, 30)
        else:
            return random.randint(200, 300)
    return random.randint(lo, hi)

def add_noise_to_km(km_diff):
    """Add realistic measurement noise — odometer isn't always read precisely"""
    noise = random.choice([-500, -200, 0, 0, 0, 200, 500])
    return max(0, km_diff + noise)

def early_change_scenario(max_km):
    """
    Unusual pattern 1: Preventive early change
    Worker replaces part way before it's due (cautious mechanic / safety protocol)
    """
    return random.randint(int(max_km * 0.3), int(max_km * 0.65))

def severely_overdue_scenario(max_km):
    """
    Unusual pattern 2: Severely overdue — budget issues / negligence
    Part is changed WAY past its lifetime (very common in government fleets)
    """
    return random.randint(int(max_km * 1.5), int(max_km * 2.8))

def double_replacement_scenario(max_km):
    """
    Unusual pattern 3: Double replacement in short period
    Part replaced, then replaced again quickly (defective part or bad install)
    """
    return random.randint(500, int(max_km * 0.15))

def seasonal_stress_scenario(max_km):
    """
    Unusual pattern 4: Seasonal stress — summer heat or winter cold accelerates wear
    km_diff looks okay but days are short (time-based degradation)
    """
    return random.randint(int(max_km * 0.4), int(max_km * 0.7))

def breakdown_scenario(max_km):
    """
    Unusual pattern 5: Emergency breakdown replacement
    Changed after failure — km far exceeded, days don't matter
    """
    return random.randint(int(max_km * 2.0), int(max_km * 3.5))

def label_needs_change(km_diff, days_diff, cfg, scenario_type):
    """
    Smart labeling that accounts for:
    - KM threshold
    - Days threshold (time-based degradation)
    - Critical parts get flagged earlier
    - Scenario context
    """
    max_km   = cfg["km"]
    max_days = cfg["days"]
    critical = cfg["critical"]

    km_ratio   = km_diff / max_km
    days_ratio = days_diff / max_days

    # Emergency / breakdown → always needs change
    if scenario_type in ("breakdown", "severely_overdue"):
        return 1

    # Critical parts: flag at 85% of either threshold
    if critical:
        if km_ratio >= 0.85 or days_ratio >= 0.85:
            return 1
        if km_ratio >= 0.75 and days_ratio >= 0.70:
            return 1

    # Normal parts: flag at 95% of either threshold
    else:
        if km_ratio >= 0.95 or days_ratio >= 0.95:
            return 1
        if km_ratio >= 0.85 and days_ratio >= 0.80:
            return 1

    # Seasonal stress: days-based degradation even at lower km
    if scenario_type == "seasonal_stress":
        if days_ratio >= 0.80:
            return 1

    # Double replacement: always 0 (just replaced)
    if scenario_type == "double_replacement":
        return 0

    # Early preventive: mechanic chose to change it early — label 0
    if scenario_type == "early_change":
        return 0

    return 0

# -----------------------------
# GENERATE DATA
# -----------------------------
data = []
start_date = datetime(2021, 1, 1)   # wider date range for more history

scenario_weights = {
    "normal":            0.50,   # standard record
    "early_change":      0.12,   # preventive early replacement
    "severely_overdue":  0.15,   # common in gov fleets — overdue
    "double_replacement":0.07,   # replaced twice fast
    "seasonal_stress":   0.08,   # time-degraded, not km-degraded
    "breakdown":         0.08,   # emergency replacement
}
scenario_types  = list(scenario_weights.keys())
scenario_wvals  = list(scenario_weights.values())

for car_id in range(1, NUM_CARS + 1):
    profile = assign_car_profile()
    current_km = random.randint(40000, 200000)

    for _ in range(RECORDS_PER_CAR):
        part = random.choice(PARTS)
        cfg  = PARTS_CONFIG[part]
        max_km   = cfg["km"]
        max_days = cfg["days"]

        scenario = random.choices(scenario_types, weights=scenario_wvals, k=1)[0]

        # --- KM DIFF based on scenario ---
        if scenario == "normal":
            km_diff = random.randint(int(max_km * 0.2), int(max_km * 1.2))
        elif scenario == "early_change":
            km_diff = early_change_scenario(max_km)
        elif scenario == "severely_overdue":
            km_diff = severely_overdue_scenario(max_km)
        elif scenario == "double_replacement":
            km_diff = double_replacement_scenario(max_km)
        elif scenario == "seasonal_stress":
            km_diff = seasonal_stress_scenario(max_km)
        elif scenario == "breakdown":
            km_diff = breakdown_scenario(max_km)

        km_diff = add_noise_to_km(km_diff)

        # --- DAYS DIFF based on scenario ---
        if scenario == "normal":
            days_diff = int((km_diff / get_km_per_day(profile)) + random.randint(-30, 30))
        elif scenario == "early_change":
            days_diff = random.randint(int(max_days * 0.25), int(max_days * 0.60))
        elif scenario == "severely_overdue":
            days_diff = random.randint(int(max_days * 1.3), int(max_days * 2.5))
        elif scenario == "double_replacement":
            days_diff = random.randint(3, 45)
        elif scenario == "seasonal_stress":
            # High days, low km — time-based wear (battery, brake fluid)
            days_diff = random.randint(int(max_days * 0.80), int(max_days * 1.3))
        elif scenario == "breakdown":
            days_diff = random.randint(int(max_days * 0.5), int(max_days * 2.0))

        days_diff = max(1, days_diff)
        km_diff   = max(0, km_diff)

        # --- LABEL ---
        needs_change = label_needs_change(km_diff, days_diff, cfg, scenario)

        # --- Record date (random within range for realism) ---
        record_date = start_date + timedelta(days=random.randint(0, 1000))

        data.append({
            "car_id":       car_id,
            "car_profile":  profile,          # useful for analysis, can drop before training
            "part":         part,
            "current_km":   current_km,
            "km_diff":      km_diff,
            "days_diff":    days_diff,
            "scenario":     scenario,          # useful for analysis, drop before training
            "needs_change": needs_change,
        })

# -----------------------------
# CREATE DATAFRAME
# -----------------------------
df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# -----------------------------
# QUICK STATS
# -----------------------------
print("=" * 55)
print("  ✅ Dataset generated successfully!")
print("=" * 55)
print(f"  Total rows         : {len(df)}")
print(f"  Unique cars        : {df['car_id'].nunique()}")
print(f"  needs_change = 1   : {df['needs_change'].sum()} ({df['needs_change'].mean()*100:.1f}%)")
print(f"  needs_change = 0   : {(df['needs_change']==0).sum()} ({(1-df['needs_change'].mean())*100:.1f}%)")
print()
print("  Scenario distribution:")
print(df['scenario'].value_counts().to_string())
print()
print("  needs_change by part:")
print(df.groupby('part')['needs_change'].mean().sort_values(ascending=False).apply(lambda x: f"{x*100:.1f}%").to_string())
print("=" * 55)

# -----------------------------
# SAVE — two versions
# -----------------------------

# Full version (with scenario + profile columns for analysis)
df.to_csv("car_maintenance_dataset_full.csv", index=False)

# Training version (clean — only model input features)
train_cols = ["car_id", "part", "current_km", "km_diff", "days_diff", "needs_change"]
df[train_cols].to_csv("car_maintenance_dataset.csv", index=False)

print()
print("  📁 car_maintenance_dataset.csv        → for model training")
print("  📁 car_maintenance_dataset_full.csv   → for analysis & debugging")
print("=" * 55)
print(df[train_cols].head(10).to_string(index=False))