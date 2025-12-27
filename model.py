#The present working and fit model
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import numpy as np

def simulate_weight_gain(
    start_weight_kg,
    start_height_cm,
    start_age,
    gender,
    daily_calories_in,
    daily_steps,
    protein_g,
    carbs_g,
    fat_g,
    metabolism_type='normal',
    simulation_days=365
):
    # --- 1. SETUP ---
    if gender == 'male':
        liv_c, liv_p, liv_y = 293, 0.4330, 5.92
    else:
        liv_c, liv_p, liv_y = 248, 0.4356, 5.09

    h_m = start_height_cm / 100
    if gender == 'male':
        lean_mass = (0.32810 * start_weight_kg) + (33.929 * h_m) - 29.5336
    else:
        lean_mass = (0.29569 * start_weight_kg) + (41.813 * h_m) - 43.2933

    if lean_mass >= start_weight_kg:
        lean_mass = start_weight_kg * 0.90

    fm = start_weight_kg - lean_mass
    ffm = lean_mass

    safe_ffm = min(ffm, 200)
    forbes_C = fm / np.exp(safe_ffm / 10.4)

    # --- 2. BASELINE ---
    rmr_0 = (liv_c * (start_weight_kg ** liv_p)) - (liv_y * start_age)
    initial_activity_kcal = daily_steps * 0.04
    m_coefficient = initial_activity_kcal / start_weight_kg

    base_rmr_pa = rmr_0 + initial_activity_kcal
    maintenance_calories = base_rmr_pa / 0.9
    non_spa_expenditure_0 = rmr_0 + initial_activity_kcal + (0.1 * maintenance_calories)

    current_weight = start_weight_kg
    current_age = start_age

    history_weight = []
    history_fm = []
    history_ffm = []

    # --- 3. SIMULATION LOOP ---
    for day in range(simulation_days):

        # Metabolism
        rmr_current = (liv_c * (current_weight ** liv_p)) - (liv_y * current_age)
        pa_current = m_coefficient * current_weight
        dit = 0.1 * daily_calories_in

        non_spa_expenditure_current = rmr_current + pa_current + dit
        delta_expenditure = non_spa_expenditure_current - non_spa_expenditure_0

        s = 0.75 if metabolism_type == 'hard_gainer' else 0.56
        spa_adjustment = (s / (1 - s)) * delta_expenditure
        ee_total = non_spa_expenditure_current + spa_adjustment

        # Energy balance
        energy_balance = daily_calories_in - ee_total

        # --- NEW: Lean gain efficiency ---
        protein_per_kg = protein_g / max(current_weight, 1)

        if protein_per_kg >= 1.6:
            protein_factor = 1.0
        elif protein_per_kg >= 1.2:
            protein_factor = 0.7
        else:
            protein_factor = 0.4

        carb_factor = 1.0 if carbs_g >= 2 * current_weight else 0.85

        lean_energy_ratio = 0.25 * protein_factor * carb_factor
        lean_energy = max(energy_balance * lean_energy_ratio, 0)
        fat_energy = energy_balance - lean_energy

        # --- Fat mass change (Forbes preserved) ---
        safe_fm = max(fm, 1.0)
        fat_denominator = 9500 + (10608 / safe_fm)
        d_fm = fat_energy / fat_denominator

        # --- Lean mass change (capped) ---
        d_ffm = min(lean_energy / 1800, 0.02)

        fm += d_fm
        ffm += d_ffm
        current_weight = fm + ffm

        if day % 365 == 0:
            current_age += 1

        history_weight.append(round(current_weight, 2))
        history_fm.append(round(fm, 2))
        history_ffm.append(round(ffm, 2))

    return {
        "days": list(range(simulation_days)),
        "weight": history_weight,
        "fat_mass": history_fm,
        "lean_mass": history_ffm
    }
