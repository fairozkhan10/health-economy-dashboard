# app.py
# Author: Fairoz Khan
# Description: Interactive dashboard for health and economic data analysis

import streamlit as st
import pandas as pd  # Import pandas as pd
from data_fetcher import fetch_health_data, fetch_economic_data
from data_processing import clean_data, transform_health_data, transform_economic_data, normalize_data, calculate_correlation
from visualization import plot_comparison_with_annotations, plot_cross_country_heatmap

# Set Streamlit page configuration
st.set_page_config(page_title="Health and Economy Dashboard", layout="wide")

st.title("🌐 Health and Economy Dashboard")

# Sidebar for user inputs
st.sidebar.header("User Inputs")

# User Input for Country Codes (Multiple Selection)
country_codes = st.sidebar.multiselect(
    "Select Country Codes (e.g., USA, IND, BRA):", 
    options=["USA", "IND", "BRA", "CAN", "GBR", "FRA", "DEU", "JPN", "CHN", "RUS"],
    default=["USA"]
)

# User Input for Health Indicator
health_indicator = st.sidebar.selectbox(
    "Select Health Indicator:",
    options=[
        "new_cases", 
        "new_deaths", 
        "total_cases", 
        "total_deaths", 
        "new_cases_per_million", 
        "new_deaths_per_million",
        "reproduction_rate",
        "icu_patients",
        "hosp_patients"
    ]
)

# User Input for Economic Indicator
economic_indicator = st.sidebar.selectbox(
    "Select Economic Indicator:",
    options=["CPIAUCSL", "GDP", "UNRATE", "DGS10", "FEDFUNDS"],
    index=0
)

# User input for the type of chart
chart_type = st.sidebar.selectbox(
    "Select Chart Type:",
    options=["Comparison Chart", "Heatmap"]
)

# User input for rolling average window size
rolling_window = st.sidebar.slider("Select Rolling Average Window (in days):", min_value=1, max_value=30, value=7)

# User input for Year Range
with st.sidebar.expander("Select Year Range"):
    year_min = 2000
    year_max = 2023
    year_range = st.slider(
        "Year Range:", 
        min_value=year_min, 
        max_value=year_max, 
        value=(2020, 2023)
    )

# Caching the data fetching and processing functions
@st.cache_data
def get_health_data():
    health_data_raw = fetch_health_data()
    if health_data_raw is not None:
        cleaned_health = clean_data(health_data_raw)
        if not cleaned_health.empty:
            health_data_transformed = transform_health_data(cleaned_health)
            if not health_data_transformed.empty:
                return normalize_data(health_data_transformed, [health_indicator])
    return None

@st.cache_data
def get_economic_data(series_ids):
    economic_data_raw = fetch_economic_data(series_ids=series_ids)
    if economic_data_raw is not None:
        cleaned_economic = clean_data(economic_data_raw)
        if not cleaned_economic.empty:
            economic_data_transformed = transform_economic_data(cleaned_economic)
            if not economic_data_transformed.empty:
                return normalize_data(economic_data_transformed, ['value'])
    return None

# Fetch and Process Health Data
with st.spinner("Fetching and processing health data..."):
    health_data_normalized = get_health_data()
    if health_data_normalized is None:
        st.error("Failed to process health data.")

# Fetch and Process Economic Data
with st.spinner("Fetching and processing economic data..."):
    economic_data_normalized = get_economic_data(series_ids=[economic_indicator])
    if economic_data_normalized is None:
        st.error("Failed to process economic data.")

# Filter Data by Year Range
if health_data_normalized is not None:
    health_filtered = health_data_normalized[
        (health_data_normalized['Year'] >= year_range[0]) &
        (health_data_normalized['Year'] <= year_range[1])
    ]
else:
    health_filtered = None

if economic_data_normalized is not None:
    economic_filtered = economic_data_normalized[
        (economic_data_normalized['Year'] >= year_range[0]) &
        (economic_data_normalized['Year'] <= year_range[1])
    ]
else:
    economic_filtered = None

# Layout: Use columns for better organization
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Visualizations")
    if chart_type == "Comparison Chart":
        if health_filtered is not None and economic_filtered is not None:
            plot_comparison_with_annotations(
                health_df=health_filtered,
                economic_df=economic_filtered,
                health_indicator=health_indicator,
                economic_indicator=economic_indicator,
                country_codes=country_codes
            )

            # Correlation Analysis
            correlation = calculate_correlation(
                health_df=health_filtered,
                economic_df=economic_filtered,
                health_col=health_indicator,
                econ_col='value'
            )
            if correlation is not None and not pd.isna(correlation):
                st.subheader("🔗 Correlation Analysis")
                st.write(f"The correlation between **{health_indicator}** and **{economic_indicator}** is **{correlation:.2f}**.")
            else:
                st.subheader("🔗 Correlation Analysis")
                st.write("Insufficient data or variability to calculate correlation.")
        else:
            st.warning("Insufficient data to generate comparison chart.")

    elif chart_type == "Heatmap":
        if health_data_normalized is not None:
            plot_cross_country_heatmap(
                health_df=health_data_normalized,
                health_indicator=health_indicator
            )
        else:
            st.warning("Insufficient health data to generate heatmap.")

with col2:
    st.header("📈 Additional Insights")
    if health_data_normalized is not None and economic_data_normalized is not None:
        # Display Health Data
        st.subheader("🔍 Health Data Sample")
        st.dataframe(health_data_normalized.head())

        # Display Economic Data
        st.subheader("🔍 Economic Data Sample")
        st.dataframe(economic_data_normalized.head())

        # Download Options
        st.subheader("💾 Download Data")
        if st.button("Download Health Data"):
            csv = health_data_normalized.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name='health_data.csv', mime='text/csv')

        if st.button("Download Economic Data"):
            csv = economic_data_normalized.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name='economic_data.csv', mime='text/csv')
    else:
        st.write("Data is insufficient to display additional insights.")

# Footer or additional layout elements can be added below as needed
