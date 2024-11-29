# data_processing.py
# Author: Fairoz Khan
# Description: Module for cleaning, transforming, and normalizing data

import pandas as pd
import logging
import streamlit as st

def clean_data_health(df):
    """Clean health data by removing duplicates and handling missing values."""
    try:
        logger.info("Starting cleaning of health data.")
        # Remove duplicate rows
        initial_shape = df.shape
        df = df.drop_duplicates()
        logger.debug(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows.")

        # Drop rows with all NaNs
        df = df.dropna(how='all')
        logger.debug("Dropped completely empty rows.")

        # Handle missing values for key indicators
        numeric_cols = [
            'new_cases', 'new_deaths', 'total_cases', 'total_deaths',
            'new_cases_per_million', 'new_deaths_per_million',
            'reproduction_rate', 'icu_patients', 'hosp_patients'
        ]
        for col in numeric_cols:
            if col in df.columns:
                missing = df[col].isna().sum()
                if missing > 0:
                    df[col] = df[col].fillna(0)  # Fill missing values with 0
                    logger.warning(f"Filled {missing} missing values in '{col}' with 0.")
        logger.info("Cleaned health data successfully.")
        return df
    except Exception as e:
        logger.error(f"Error cleaning health data: {e}")
        st.error(f"Error cleaning health data: {e}")
        return pd.DataFrame()

def transform_health_data(df):
    """Transform health data by aggregating key indicators annually."""
    try:
        logger.info("Starting transformation of health data.")

        # Ensure 'date' column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            logger.debug("Converted 'date' to datetime.")

        # Extract Year
        df['Year'] = df['date'].dt.year

        # Select relevant columns
        relevant_cols = [
            'iso_code', 'location', 'continent', 'date', 'Year',
            'new_cases', 'new_deaths', 'total_cases', 'total_deaths',
            'new_cases_per_million', 'new_deaths_per_million',
            'reproduction_rate', 'icu_patients', 'hosp_patients'
        ]
        df = df[relevant_cols]
        logger.debug(f"Selected relevant columns: {relevant_cols}")

        # Group by 'iso_code' and 'Year' and calculate mean of numeric columns
        numeric_cols = [
            'new_cases', 'new_deaths', 'total_cases', 'total_deaths',
            'new_cases_per_million', 'new_deaths_per_million',
            'reproduction_rate', 'icu_patients', 'hosp_patients'
        ]
        df_transformed = df.groupby(['iso_code', 'location', 'continent', 'Year'])[numeric_cols].mean().reset_index()
        logger.debug(f"Transformed health data sample:\n{df_transformed.head()}")

        logger.info("Transformed health data successfully.")
        return df_transformed
    except Exception as e:
        logger.error(f"Error transforming health data: {e}")
        st.error(f"Error transforming health data: {e}")
        return pd.DataFrame()

def transform_economic_data(df):
    """Transform economic data from World Bank API."""
    try:
        logger.info("Starting transformation of economic data.")
        
        # Rename columns for clarity
        df = df.rename(columns={
            'countryiso3code': 'iso_code',
            'date': 'Year',
            'value': 'value'
        })
        
        # Convert 'Year' to numeric
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        # Convert 'value' to numeric
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Drop rows with missing 'Year' or 'value'
        df = df.dropna(subset=['Year', 'value'])
        
        # Select relevant columns
        df = df[['iso_code', 'Year', 'value']]
        
        logger.info("Transformed economic data successfully.")
        return df
    except Exception as e:
        logger.error(f"Error transforming economic data: {e}")
        st.error(f"Error transforming economic data: {e}")
        return pd.DataFrame()

def normalize_data(df, columns):
    """Normalize specified columns in the DataFrame."""
    try:
        logger.info(f"Starting normalization for columns: {columns}")
        for column in columns:
            if column in df.columns:
                # Handle missing values by filling them with the column mean
                missing_before = df[column].isna().sum()
                df[column] = df[column].fillna(df[column].mean())
                missing_after = df[column].isna().sum()
                if missing_before > 0:
                    logger.warning(f"Filled {missing_before} missing values in column '{column}' with the mean.")

                min_val = df[column].min()
                max_val = df[column].max()
                if pd.notnull(min_val) and pd.notnull(max_val) and max_val - min_val != 0:
                    df[column] = (df[column] - min_val) / (max_val - min_val)
                    logger.debug(f"Normalized column '{column}'.")
                else:
                    df[column] = 0.0  # Avoid division by zero if all values are the same or invalid
                    logger.warning(f"Normalization skipped for column '{column}' due to constant or invalid values.")
            else:
                logger.warning(f"Column '{column}' not found in DataFrame. Skipping normalization for this column.")
        logger.info("Data normalization completed.")
        return df
    except Exception as e:
        logger.error(f"Error normalizing data: {e}")
        st.error(f"Error normalizing data: {e}")
        return pd.DataFrame()

def calculate_correlation(health_df, economic_df, health_col, econ_col):
    """Calculate the correlation between a health indicator and an economic indicator."""
    try:
        logger.info(f"Calculating correlation between '{health_col}' and '{econ_col}'.")
        # Merge on 'Year' and 'iso_code'
        merged = pd.merge(
            health_df,
            economic_df,
            on=['iso_code', 'Year'],
            how='inner',
            suffixes=('_health', '_econ')
        )
        logger.debug(f"Merged data for correlation calculation:\n{merged.head()}")

        if merged.shape[0] < 2:
            logger.warning("Insufficient data points for correlation.")
            return None

        # Drop rows with NaN in the specified columns
        merged = merged.dropna(subset=[health_col, econ_col])
        if merged.empty:
            logger.warning("No data available after dropping NaN values for correlation calculation.")
            return None

        # Calculate correlation
        correlation = merged[health_col].corr(merged[econ_col])
        logger.info(f"Calculated correlation: {correlation}")
        return correlation
    except Exception as e:
        logger.error(f"Error calculating correlation: {e}")
        st.error(f"Error calculating correlation: {e}")
        return None

# Configure Logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

    logger.info("\nTesting clean_data_health...")
    cleaned_health = clean_data_health(health_mock)
    logger.info(cleaned_health)

    logger.info("\nTesting transform_health_data...")
    health_transformed = transform_health_data(cleaned_health)
    logger.info(health_transformed)

    logger.info("\nTesting transform_economic_data...")
    economic_transformed = transform_economic_data(economic_mock)
    logger.info(economic_transformed)

    logger.info("\nTesting normalize_data...")
    normalized_health = normalize_data(health_transformed, ['new_cases'])
    logger.info(normalized_health)

    logger.info("\nTesting calculate_correlation...")
    correlation = calculate_correlation(health_transformed, economic_transformed, 'new_cases', 'value')
    logger.info(f"Correlation: {correlation}")
