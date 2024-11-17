# data_processing.py
# Author: Fairoz Khan
# Description: Module for cleaning, transforming, and normalizing data

import pandas as pd
import streamlit as st  # Needed for the clean_data function to print warnings


def clean_data(df):
    """Clean data by removing duplicates and dropping irrelevant columns, excluding 'data'."""
    try:
        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Remove rows that are completely empty
        df = df.dropna(how='all')
        
        # Ensure 'data' column exists and contains lists; replace NaN or non-list with empty lists
        if 'data' in df.columns:
            df['data'] = df['data'].apply(lambda x: x if isinstance(x, list) else [])
        else:
            st.warning("Warning: 'data' column not found in the DataFrame.")
            df['data'] = [[] for _ in range(len(df))]  # Assign a list of empty lists
        
        # Identify columns with complex data types (lists, dicts, sets), excluding 'data'
        complex_cols = [col for col in df.columns if col != 'data' and df[col].apply(lambda x: isinstance(x, (list, dict, set))).any()]
        if complex_cols:
            print(f"Columns with complex data types (to be dropped): {complex_cols}")
            df = df.drop(columns=complex_cols)
        
        # Remove duplicate rows, excluding 'data' column to avoid unhashable types
        if 'data' in df.columns:
            df = df.drop_duplicates(subset=[col for col in df.columns if col != 'data'])
        else:
            df = df.drop_duplicates()
        
        print("Cleaned data sample:\n", df.head())
        return df
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return pd.DataFrame()


def transform_health_data(df):
    """Transform health data by exploding and normalizing the 'data' column."""
    try:
        print("Initial health data columns:", df.columns)
        if 'data' not in df.columns:
            print("Error: 'data' column not found in health data.")
            return pd.DataFrame()

        # Explode the 'data' column to have one row per record
        df_exploded = df.explode('data').reset_index(drop=True)
        print("After exploding 'data' column:", df_exploded.shape)

        # Normalize the nested 'data' dictionaries
        data_expanded = pd.json_normalize(df_exploded['data'])
        print("Normalized 'data' column:", data_expanded.shape)

        # Concatenate the main dataframe with the expanded data
        df_combined = pd.concat([df_exploded.drop(columns=['data']), data_expanded], axis=1)
        print("Combined dataframe shape:", df_combined.shape)

        # Check if 'date' column exists
        if 'date' not in df_combined.columns:
            print("Error: 'date' column not found after normalization.")
            return pd.DataFrame()

        # Convert 'date' to datetime and extract 'Year'
        df_combined['date'] = pd.to_datetime(df_combined['date'], errors='coerce')
        df_combined['Year'] = df_combined['date'].dt.year

        # Identify numeric columns for aggregation, excluding 'Year'
        numeric_cols = [col for col in df_combined.select_dtypes(include=['number']).columns if col != 'Year']
        print("Numeric columns for aggregation:", numeric_cols)

        # Group by 'country_code' and 'Year' and calculate mean of numeric columns
        df_transformed = df_combined.groupby(['country_code', 'Year'])[numeric_cols].mean().reset_index()
        print("Transformed health data sample:\n", df_transformed.head())
        return df_transformed
    except Exception as e:
        print(f"Error transforming health data: {e}")
        return pd.DataFrame()


def transform_economic_data(df):
    """Transform economic data by extracting year and grouping by series_id and year."""
    try:
        print("Initial economic data columns:", df.columns)
        if 'Year' in df.columns:
            print("'Year' column already exists. Skipping creation.")
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['Year'] = df['date'].dt.year
        else:
            print("Error: 'date' column not found in economic data.")
            return pd.DataFrame()

        # Ensure 'value' column is numeric
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
        else:
            print("Error: 'value' column not found in economic data.")
            return pd.DataFrame()

        # Identify numeric columns for aggregation, excluding 'Year'
        numeric_cols = [col for col in df.select_dtypes(include=['number']).columns if col != 'Year']
        print("Numeric columns for aggregation:", numeric_cols)

        # Group by 'series_id' and 'Year' and calculate mean of numeric columns
        df_transformed = df.groupby(['series_id', 'Year'])[numeric_cols].mean().reset_index()
        print("Transformed economic data sample:\n", df_transformed.head())
        return df_transformed
    except Exception as e:
        print(f"Error transforming economic data: {e}")
        return pd.DataFrame()


def normalize_data(df, columns):
    """Normalize specified columns in the DataFrame."""
    try:
        for column in columns:
            if column in df.columns:
                min_val = df[column].min()
                max_val = df[column].max()
                if pd.notnull(min_val) and pd.notnull(max_val) and max_val - min_val != 0:
                    df[column] = (df[column] - min_val) / (max_val - min_val)
                else:
                    df[column] = 0.0  # Avoid division by zero if all values are the same or invalid
        print("Data after normalization:\n", df.head())
        return df
    except Exception as e:
        print(f"Error normalizing data: {e}")
        return pd.DataFrame()


def calculate_correlation(health_df, economic_df, health_col, econ_col):
    """Calculate the correlation between a health indicator and an economic indicator."""
    try:
        # Merge on 'Year'
        merged = pd.merge(health_df, economic_df, on='Year', how='inner', suffixes=('_health', '_econ'))
        print("Merged data for correlation calculation:\n", merged.head())

        if merged.shape[0] < 2:
            print("Insufficient data points for correlation.")
            return None

        # Calculate correlation
        correlation = merged[[health_col, econ_col]].corr().iloc[0, 1]
        return correlation
    except Exception as e:
        print(f"Error calculating correlation: {e}")
        return None


# Test block
if __name__ == "__main__":
    # Mock health data with nested 'data' column
    health_mock = pd.DataFrame({
        'country_code': ['USA', 'IND'],
        'continent': ['North America', 'Asia'],
        'location': ['United States', 'India'],
        'population': [331002651, 1380004385],
        'population_density': [36.0, 464.0],
        'median_age': [38.3, 28.4],
        'aged_65_older': [16.5, 5.1],
        'aged_70_older': [10.5, 3.0],
        'gdp_per_capita': [65112.0, 2100.0],
        'cardiovasc_death_rate': [300.0, 200.0],
        'diabetes_prevalence': [10.5, 8.0],
        'handwashing_facilities': [99.0, 75.0],
        'hospital_beds_per_thousand': [2.8, 0.5],
        'life_expectancy': [78.54, 69.42],
        'human_development_index': [0.920, 0.645],
        'data': [
            [
                {'date': '2020-01-01', 'new_cases': 0, 'new_deaths': 0},
                {'date': '2020-01-02', 'new_cases': 1, 'new_deaths': 0}
            ],
            [
                {'date': '2020-01-01', 'new_cases': 0, 'new_deaths': 0},
                {'date': '2020-01-02', 'new_cases': 2, 'new_deaths': 0}
            ]
        ],
        'extreme_poverty': [9.2, 20.3],
        'female_smokers': [12.0, 5.0],
        'male_smokers': [14.0, 7.0]
    })

    # Mock economic data
    economic_mock = pd.DataFrame({
        'series_id': ['CPIAUCSL', 'CPIAUCSL'],
        'date': ['2020-01-01', '2021-01-01'],
        'value': [257.5, 260.0],
        'realtime_start': ['2020-01-01', '2021-01-01'],
        'realtime_end': ['2020-01-02', '2021-01-02']
    })

    print("\nTesting clean_data...")
    cleaned_health = clean_data(health_mock)
    print(cleaned_health)

    print("\nTesting transform_health_data...")
    health_transformed = transform_health_data(cleaned_health)
    print(health_transformed)

    print("\nTesting transform_economic_data...")
    economic_transformed = transform_economic_data(economic_mock)
    print(economic_transformed)

    print("\nTesting normalize_data...")
    normalized_health = normalize_data(health_transformed, ['new_cases'])
    print(normalized_health)

    print("\nTesting calculate_correlation...")
    correlation = calculate_correlation(health_transformed, economic_transformed, 'new_cases', 'value')
    print("Correlation:", correlation)
