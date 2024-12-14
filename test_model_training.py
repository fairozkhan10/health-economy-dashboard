# test_model_training.py

import pandas as pd
from machine_learning import train_economic_model

# Mock DataFrames
# Create small DataFrames with sufficient data for testing

# Health DataFrame
health_data = {
    'iso_code': ['USA', 'USA', 'USA', 'USA'],
    'location': ['United States'] * 4,
    'continent': ['North America'] * 4,
    'Year': [2020, 2021, 2022, 2023],
    'new_cases': [1000, 2000, 1500, 1800],
    'new_deaths': [50, 60, 55, 58],
    'total_cases': [50000, 52000, 53500, 55300],
    'total_deaths': [2000, 2060, 2115, 2173],
    'new_cases_per_million': [300, 320, 310, 330],
    'new_deaths_per_million': [15, 18, 16, 17],
    'reproduction_rate': [1.2, 1.1, 1.3, 1.25],
    'icu_patients': [100, 110, 105, 115],
    'hosp_patients': [500, 550, 525, 575],
    'population_density': [36, 36, 36, 36],
    'median_age': [38, 39, 38.5, 39],
    'aged_65_older': [16, 16.5, 16.2, 16.7],
    'aged_70_older': [10, 10.2, 10.1, 10.3],
    'gdp_per_capita': [60000, 61000, 62000, 63000],
    'cardiovasc_death_rate': [200, 205, 202, 208],
    'diabetes_prevalence': [10, 10.5, 10.3, 10.7],
    'handwashing_facilities': [95, 95, 95, 95],
    'hospital_beds_per_thousand': [3.5, 3.5, 3.5, 3.5],
    'life_expectancy': [78, 78.2, 78.1, 78.3],
    'human_development_index': [0.920, 0.921, 0.922, 0.923],
    'extreme_poverty': [0.5, 0.5, 0.5, 0.5],
    'female_smokers': [14, 14.2, 14.1, 14.3],
    'male_smokers': [20, 20.1, 20.2, 20.3]
}
health_df = pd.DataFrame(health_data)

# Economic DataFrame
economic_data = {
    'iso_code': ['USA', 'USA', 'USA', 'USA'],
    'Year': [2020, 2021, 2022, 2023],
    'value': [21000000000000, 22000000000000, 23000000000000, 24000000000000]  # Example GDP data
}
economic_df = pd.DataFrame(economic_data)

# Train the model
rmse, r2 = train_economic_model(
    health_df=health_df,
    economic_df=economic_df,
    target_col='value',
    indicator_code='NY.GDP.MKTP.CD'
)

if rmse is not None and r2 is not None:
    print(f"Model trained successfully with RMSE: {rmse}, R²: {r2}")
else:
    print("Model training failed.")
