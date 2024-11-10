# app.py
# Author: Fairoz Khan
# Description: Main dashboard app integrating data fetching, processing, and visualization

import streamlit as st
from data_fetcher import fetch_health_data as fetch_health_data_uncached, fetch_economic_data as fetch_economic_data_uncached
from data_processing import clean_data, transform_health_data, transform_economic_data
from visualization import plot_health_data, plot_economic_data

@st.cache_data(show_spinner=False)
def fetch_health_data():
    return fetch_health_data_uncached()

@st.cache_data(show_spinner=False)
def fetch_economic_data(series_ids=["CPIAUCSL"]):
    return fetch_economic_data_uncached(series_ids)

st.title("Health and Economy Dashboard")

# User Input for Country Code
country_code = st.text_input("Enter Country Code (e.g., USA, IND, BRA):", value="USA")

# User Input for Health Indicator
health_indicator = st.selectbox(
    "Select Health Indicator:",
    options=['new_cases', 'new_deaths', 'total_cases', 'total_deaths']
)

# User Input for Economic Indicator
economic_indicator = st.selectbox(
    "Select Economic Indicator:",
    options=['CPIAUCSL', 'GDP']
)

# Fetch Health Data
with st.spinner('Fetching health data...'):
    health_data_raw = fetch_health_data()
    if health_data_raw is not None:
        st.write("Raw Health Data Sample:")
        st.write(health_data_raw.head())
    else:
        st.error("Failed to fetch health data.")

# Process Health Data
if health_data_raw is not None:
    with st.spinner('Processing health data...'):
        health_data = transform_health_data(health_data_raw)
        if health_data is not None:
            st.write("Transformed Health Data Sample:")
            st.write(health_data.head())
            st.write("Health Data Columns:", list(health_data.columns))
        else:
            st.error("Health data transformation failed.")
else:
    health_data = None

# Proceed only if health_data is not None and not empty
if health_data is not None and not health_data.empty:
    # Check if the indicator exists in the data
    if health_indicator in health_data.columns:
        st.subheader(f"Health Data for {country_code}")
        plot_health_data(health_data, indicator=health_indicator, country_code=country_code)
    else:
        st.error(f"Indicator '{health_indicator}' not found in the health data.")
        st.write("Available indicators:", list(health_data.columns))
else:
    st.write("Health data could not be retrieved or is empty.")

# Fetch Economic Data
with st.spinner('Fetching economic data...'):
    economic_data_raw = fetch_economic_data(series_ids=[economic_indicator])
    if economic_data_raw is not None:
        st.write("Raw Economic Data Sample:")
        st.write(economic_data_raw.head())
    else:
        st.error("Failed to fetch economic data.")

# Process Economic Data
if economic_data_raw is not None:
    with st.spinner('Processing economic data...'):
        economic_data = transform_economic_data(economic_data_raw, date_column='date')
        if economic_data is not None:
            economic_data = clean_data(economic_data)
            st.write("Transformed Economic Data Sample:")
            st.write(economic_data.head())
        else:
            st.error("Economic data transformation failed.")
else:
    economic_data = None

# Proceed only if economic_data is not None and not empty
if economic_data is not None and not economic_data.empty:
    st.subheader(f"Economic Data: {economic_indicator}")
    plot_economic_data(economic_data, indicator='value')
else:
    st.write("Economic data could not be retrieved or is empty.")
