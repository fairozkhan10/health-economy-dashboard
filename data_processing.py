# data_processing.py
# Author: Fairoz Khan
# Description: Module for cleaning, transforming, and normalizing data

import pandas as pd
import logging
import streamlit as st  # Needed for the clean_data function to print warnings


def clean_data(df):
    """Clean data by removing duplicates and dropping irrelevant columns, excluding 'data'."""
    try:
        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        logger.debug("Removed duplicate columns.")

        # Remove rows that are completely empty
        df = df.dropna(how='all')
        logger.debug("Dropped completely empty rows.")

        # Ensure 'data' column exists and contains lists; replace NaN or non-list with empty lists
        if 'data' in df.columns:
            df['data'] = df['data'].apply(lambda x: x if isinstance(x, list) else [])
            logger.debug("'data' column processed to ensure it contains lists.")
        else:
            logger.warning("Warning: 'data' column not found in the DataFrame.")
            st.warning("Warning: 'data' column not found in the DataFrame.")
            df['data'] = [[] for _ in range(len(df))]  # Assign a list of empty lists

        # Identify columns with complex data types (lists, dicts, sets), excluding 'data'
        complex_cols = [col for col in df.columns if col != 'data' and df[col].apply(lambda x: isinstance(x, (list, dict, set))).any()]
        if complex_cols:
            logger.info(f"Columns with complex data types (to be dropped): {complex_cols}")
            df = df.drop(columns=complex_cols)
            logger.debug("Dropped columns with complex data types.")
        else:
            logger.debug("No columns with complex data types found.")

        # Remove duplicate rows, excluding 'data' column to avoid unhashable types
        if 'data' in df.columns:
            df = df.drop_duplicates(subset=[col for col in df.columns if col != 'data'])
        else:
            df = df.drop_duplicates()
        logger.debug("Dropped duplicate rows.")

        logger.info("Cleaned data successfully.")
        return df
    except Exception as e:
        logger.error(f"Error cleaning data: {e}")
        st.error(f"Error cleaning data: {e}")
        return pd.DataFrame()


def transform_health_data(df):
    """Transform health data by exploding and normalizing the 'data' column."""
    try:
        logger.info("Starting transformation of health data.")
        logger.debug(f"Initial health data columns: {df.columns.tolist()}")

        if 'data' not in df.columns:
            logger.error("Error: 'data' column not found in health data.")
            st.error("Error: 'data' column not found in health data.")
            return pd.DataFrame()

        # Explode the 'data' column to have one row per record
        df_exploded = df.explode('data').reset_index(drop=True)
        logger.debug(f"After exploding 'data' column: {df_exploded.shape}")

        # Normalize the nested 'data' dictionaries
        data_expanded = pd.json_normalize(df_exploded['data'])
        logger.debug(f"Normalized 'data' column: {data_expanded.shape}")

        # Concatenate the main dataframe with the expanded data
        df_combined = pd.concat([df_exploded.drop(columns=['data']), data_expanded], axis=1)
        logger.debug(f"Combined dataframe shape: {df_combined.shape}")

        # Check if 'date' column exists
        if 'date' not in df_combined.columns:
            logger.error("Error: 'date' column not found after normalization.")
            st.error("Error: 'date' column not found after normalization.")
            return pd.DataFrame()

        # Convert 'date' to datetime and extract 'Year'
        df_combined['date'] = pd.to_datetime(df_combined['date'], errors='coerce')
        df_combined['Year'] = df_combined['date'].dt.year
        logger.debug("Converted 'date' to datetime and extracted 'Year'.")

        # Identify numeric columns for aggregation, excluding 'Year'
        numeric_cols = [col for col in df_combined.select_dtypes(include=['number']).columns if col != 'Year']
        logger.info(f"Numeric columns for aggregation: {numeric_cols}")

        # Group by 'country_code' and 'Year' and calculate mean of numeric columns
        df_transformed = df_combined.groupby(['country_code', 'Year'])[numeric_cols].mean().reset_index()
        logger.debug(f"Transformed health data sample:\n{df_transformed.head()}")

        logger.info("Transformed health data successfully.")
        return df_transformed
    except Exception as e:
        logger.error(f"Error transforming health data: {e}")
        st.error(f"Error transforming health data: {e}")
        return pd.DataFrame()


def transform_economic_data(df):
    """Transform economic data by extracting year and grouping by series_id and year."""
    try:
        logger.info("Starting transformation of economic data.")
        logger.debug(f"Initial economic data columns: {df.columns.tolist()}")

        if 'Year' in df.columns:
            logger.debug("'Year' column already exists. Skipping creation.")
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['Year'] = df['date'].dt.year
            logger.debug("Converted 'date' to datetime and extracted 'Year'.")
        else:
            logger.error("Error: 'date' column not found in economic data.")
            st.error("Error: 'date' column not found in economic data.")
            return pd.DataFrame()

        # Ensure 'value' column is numeric
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            logger.debug("Ensured 'value' column is numeric.")
        else:
            logger.error("Error: 'value' column not found in economic data.")
            st.error("Error: 'value' column not found in economic data.")
            return pd.DataFrame()

        # Identify numeric columns for aggregation, excluding 'Year'
        numeric_cols = [col for col in df.select_dtypes(include=['number']).columns if col != 'Year']
        logger.info(f"Numeric columns for aggregation: {numeric_cols}")

        # Group by 'series_id' and 'Year' and calculate mean of numeric columns
        df_transformed = df.groupby(['series_id', 'Year'])[numeric_cols].mean().reset_index()
        logger.debug(f"Transformed economic data sample:\n{df_transformed.head()}")

        logger.info("Transformed economic data successfully.")
        return df_transformed
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
        # Merge on 'Year'
        merged = pd.merge(health_df, economic_df, on='Year', how='inner', suffixes=('_health', '_econ'))
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
        correlation = merged[[health_col, econ_col]].corr().iloc[0, 1]
        logger.info(f"Calculated correlation: {correlation}")
        return correlation
    except Exception as e:
        logger.error(f"Error calculating correlation: {e}")
        st.error(f"Error calculating correlation: {e}")
        return None


# Configure Logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO or WARNING to reduce verbosity
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

    logger.info("\nTesting clean_data...")
    cleaned_health = clean_data(health_mock)
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
