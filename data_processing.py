# data_processing.py
# Author: Fairoz Khan
# Description: Module for cleaning and transforming health and economic data

import pandas as pd
import streamlit as st  # Import Streamlit for caching

@st.cache_data(show_spinner=False)
def clean_data(df):
    """Clean data by removing NaN values, duplicates, and complex objects."""
    # Drop columns with lists, dictionaries, or other complex objects
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict, set))).any():
            df = df.drop(columns=[col])
    df = df.dropna().drop_duplicates()
    return df

@st.cache_data(show_spinner=False)
def transform_health_data(df):
    """Transform health data by expanding the data column and processing."""
    # Check if 'data' column exists
    if 'data' not in df.columns:
        st.error("Error: 'data' column not found in the health data.")
        return df

    # Explode the 'data' column so that each row corresponds to a date
    df_exploded = df.explode('data').reset_index(drop=True)

    # Normalize the 'data' column to expand nested dictionaries into columns
    data_normalized = pd.json_normalize(df_exploded['data'])

    # Concatenate the normalized data with the exploded DataFrame
    df_combined = pd.concat([df_exploded.drop(columns=['data']), data_normalized], axis=1)

    # Convert 'date' to datetime and extract 'Year'
    df_combined['date'] = pd.to_datetime(df_combined['date'], errors='coerce')
    df_combined['Year'] = df_combined['date'].dt.year

    # Remove rows with NaN 'Year' values
    df_combined = df_combined.dropna(subset=['Year'])

    # Select numeric columns for aggregation
    numeric_cols = df_combined.select_dtypes(include='number').columns.tolist()
    # Ensure 'country_code' and 'Year' are included in the DataFrame
    group_cols = ['country_code', 'Year']
    numeric_cols = [col for col in numeric_cols if col not in group_cols]
    # Aggregate data by 'country_code' and 'Year' on numeric columns
    df_grouped = df_combined[group_cols + numeric_cols].groupby(group_cols).mean().reset_index()

    return df_grouped

@st.cache_data(show_spinner=False)
def transform_economic_data(df, date_column='date'):
    """Transform economic data by extracting year and grouping by series_id and year."""
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df['Year'] = df[date_column].dt.year
    # Convert 'value' column to numeric
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    # Aggregate by 'series_id' and 'Year' to get annual data per series
    df_grouped = df.groupby(['series_id', 'Year'])['value'].mean().reset_index()
    return df_grouped

# Remove or comment out the test block
