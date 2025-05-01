# 1. Data Pipeline: Ingest, Process, Store

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path
from datetime import date

# Define parameters
n_flights = 100  # Number of synthetic flights
start_date = datetime(2020, 1, 1)
end_date = datetime.today()

print(f"Generating flights from {start_date.date()} to {end_date.date()}")

# Sample data (dynamic handling)
output_dir = Path("../output")
output_dir.mkdir(parents=True, exist_ok=True)

# Load airports and aircraft types dynamically if available
try:
    external_config = pd.read_json("../config/data_config.json")
    airports = external_config["airports"]
    aircraft_types = external_config["aircraft_types"]
except Exception:
    airports = ['FRA', 'MUC', 'BER', 'CDG', 'LHR', 'ZRH']
    aircraft_types = {
        'A320': 2500,
        'A350': 5800,
        'B737': 2400,
        'B787': 5200
    }

saf_blends = [0, 10, 20, 50]

# Random date generator
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Generate synthetic flights
flights = []
for i in range(n_flights):
    origin, dest = random.sample(airports, 2)
    aircraft = random.choice(list(aircraft_types.keys()))
    duration_hr = round(random.uniform(1.0, 12.0), 2)
    fuel_kg = duration_hr * aircraft_types[aircraft]
    saf_pct = random.choices(saf_blends, weights=[0.5, 0.3, 0.15, 0.05])[0]
    co2_emissions_kg = fuel_kg * 3.16 * (1 - saf_pct / 100)

    flights.append({
        'flight_id': f'DLH{i:04}',
        'date': random_date(start_date, end_date),
        'origin': origin,
        'destination': dest,
        'aircraft_type': aircraft,
        'flight_duration_hr': duration_hr,
        'fuel_burn_kg': fuel_kg,
        'SAF_blend_pct': saf_pct,
        'co2_emissions_kg': co2_emissions_kg
    })

# Convert to DataFrame
df = pd.DataFrame(flights)

# Save to CSV in the output folder
df.to_csv(output_dir / 'simulated_flight_emissions.csv', index=False)

# EU ETS Coverage - is the flight entirely within the EEA?
eea_airports = {
    'FRA': 'DE', 'MUC': 'DE', 'BER': 'DE',
    'CDG': 'FR', 'LHR': 'UK', 'AMS': 'NL',
    'MAD': 'ES', 'BCN': 'ES', 'FCO': 'IT', 'ZRH': 'CH'
}

eea_countries = ['DE', 'FR', 'NL', 'ES', 'IT']

df['origin_country'] = df['origin'].map(eea_airports)
df['destination_country'] = df['destination'].map(eea_airports)

df['in_eea'] = df.apply(
    lambda row: row['origin_country'] in eea_countries and row['destination_country'] in eea_countries,
    axis=1
)

# Step 3: Assign operator
try:
    operators = pd.read_json("../config/operators.json")
except Exception:
    operators = pd.DataFrame([
        {'id': 'DLH', 'name': 'Lufthansa'},
        {'id': 'AFR', 'name': 'Air France'},
        {'id': 'BAW', 'name': 'British Airways'},
        {'id': 'KLM', 'name': 'KLM Royal Dutch'}
    ])

df['operator_id'] = np.random.choice(operators['id'], size=len(df))
df = df.merge(operators, how='left', left_on='operator_id', right_on='id')
df.rename(columns={'name': 'operator_name'}, inplace=True)
df.drop(columns=['id'], inplace=True)

# Step 4: Simulate verification and dynamic compliance

def simulate_verification(row):
    if not row['in_eea']:
        return False
    if row['SAF_blend_pct'] > 20:
        return np.random.rand() > 0.1
    if row['fuel_burn_kg'] > 20000:
        return np.random.rand() > 0.1
    return np.random.rand() > 0.2

df['verified'] = df.apply(simulate_verification, axis=1)

df['operator_compliant'] = df.apply(
    lambda row: row['verified'] and (np.random.rand() > 0.05),
    axis=1
)

# Step 5: Determine if offset is required
df['offset_required'] = df.apply(
    lambda row: row['in_eea'] and not row['operator_compliant'] and row['verified'],
    axis=1
)

# Store to a versioned CSV
filename = output_dir / f"flights_{date.today()}.csv"
df.to_csv(filename, index=False)

# Reporting summary
summary = {
    'total_flights': len(df),
    'eea_coverage_pct': df['in_eea'].mean() * 100,
    'verified_pct': df['verified'].mean() * 100,
    'compliant_pct': df['operator_compliant'].mean() * 100,
    'total_emissions_tonnes': df['co2_emissions_kg'].sum() / 1000,
    'offset_required_tonnes': df.loc[df['offset_required'], 'co2_emissions_kg'].sum() / 1000
}

for k, v in summary.items():
    print(f"{k.replace('_', ' ').title()}: {v:.2f}")

# Preview columns and sample rows
print(df.columns)
print(df[['operator_name', 'co2_emissions_kg', 'in_eea', 'verified', 'offset_required']].head())
