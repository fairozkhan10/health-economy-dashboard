# app.py
# Author: Fairoz Khan
# Description: Interactive dashboard for health and economic data analysis with ML predictions

import streamlit as st
import pandas as pd
import logging
from data_fetcher import fetch_health_data, fetch_economic_data
from data_processing import (
    clean_data_health,
    transform_health_data,
    transform_economic_data,
    normalize_data,
    calculate_correlation
)
from visualization import plot_comparison_with_annotations, plot_cross_country_heatmap
from machine_learning import train_economic_model, predict_economic_indicator, load_model

# Configure Logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set Streamlit page configuration
st.set_page_config(page_title="Health and Economy Dashboard", layout="wide")

st.title("🌐 Health and Economy Dashboard")

# Sidebar for user inputs
st.sidebar.header("User Inputs")

# Fetch available country codes from OWID data
@st.cache_data
def get_available_countries():
    health_data_raw = fetch_health_data()
    if health_data_raw is not None:
        countries = sorted(health_data_raw['iso_code'].dropna().unique())
        return countries
    else:
        return []

available_countries = get_available_countries()

# User Input for Country Codes (Multiple Selection)
country_codes = st.sidebar.multiselect(
    "Select Country Codes:",
    options=available_countries,
    default=["USA", "IND", "BRA"]
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

# User Input for Economic Indicator (used for visualization)
economic_indicators = {
    "GDP (Current US$)": "NY.GDP.MKTP.CD",
    "GDP per Capita (Current US$)": "NY.GDP.PCAP.CD",
    "GDP Growth (Annual %)": "NY.GDP.MKTP.KD.ZG",
    "Inflation, Consumer Prices (Annual %)": "FP.CPI.TOTL.ZG",
    "Unemployment Rate (%)": "SL.UEM.TOTL.ZS",
    "Health Expenditure per Capita (Current US$)": "SH.XPD.CHEX.PC.CD",
    "Health Expenditure (% of GDP)": "SH.XPD.CHEX.GD.ZS",
    "Poverty Headcount Ratio (% of Population)": "SI.POV.DDAY",
    "Gini Index": "SI.POV.GINI",
    "Life Expectancy at Birth (Years)": "SP.DYN.LE00.IN",
    "CO₂ Emissions (Metric Tons per Capita)": "EN.ATM.CO2E.PC",
    "Access to Electricity (% of Population)": "EG.ELC.ACCS.ZS",
    "Population Growth (Annual %)": "SP.POP.GROW",
    "Urban Population (% of Total Population)": "SP.URB.TOTL.IN.ZS",
    "Labor Force Participation Rate (%)": "SL.TLF.CACT.ZS",
    "Government Expenditure on Education (% of GDP)": "SE.XPD.TOTL.GD.ZS",
}

economic_indicator_name = st.sidebar.selectbox(
    "Select Economic Indicator for Visualization:",
    options=list(economic_indicators.keys()),
    index=0
)
economic_indicator_code = economic_indicators[economic_indicator_name]

# User input for the type of chart
chart_type = st.sidebar.selectbox(
    "Select Chart Type:",
    options=["Comparison Chart", "Heatmap"]
)

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
        cleaned_health = clean_data_health(health_data_raw)
        if not cleaned_health.empty:
            health_data_transformed = transform_health_data(cleaned_health)
            if not health_data_transformed.empty:
                return health_data_transformed
    return None

@st.cache_data
def get_economic_data(country_codes, indicator_id):
    economic_data_raw = fetch_economic_data(country_codes=country_codes, indicator_id=indicator_id)
    if economic_data_raw is not None:
        economic_data_transformed = transform_economic_data(economic_data_raw)
        if not economic_data_transformed.empty:
            return economic_data_transformed
    return None

# Fetch and Process Health Data
with st.spinner("Fetching and processing health data..."):
    health_data = get_health_data()
    if health_data is None:
        st.error("Failed to process health data.")

# Fetch and Process Economic Data for Visualization
with st.spinner("Fetching and processing economic data for visualization..."):
    economic_data = get_economic_data(country_codes=country_codes, indicator_id=economic_indicator_code)
    if economic_data is None:
        st.error("Failed to process economic data.")

# User selects the economic indicator to predict
st.sidebar.header("📈 Predictive Modeling")

st.sidebar.subheader("Select Economic Indicator to Predict")
prediction_economic_indicator_name = st.sidebar.selectbox(
    "Select Economic Indicator to Predict:",
    options=list(economic_indicators.keys()),
    index=0
)
prediction_economic_indicator_code = economic_indicators[prediction_economic_indicator_name]

# Fetch and Process Economic Data for Prediction
with st.spinner("Fetching and processing economic data for prediction..."):
    prediction_economic_data = get_economic_data(country_codes=country_codes, indicator_id=prediction_economic_indicator_code)
    if prediction_economic_data is None:
        st.error("Failed to process economic data for prediction.")

# Filter Data by Year Range and Country Codes
if health_data is not None:
    health_filtered = health_data[
        (health_data['Year'] >= year_range[0]) &
        (health_data['Year'] <= year_range[1]) &
        (health_data['iso_code'].isin(country_codes))
    ]
    health_filtered = normalize_data(health_filtered, [health_indicator])
    logger.debug(f"Health data filtered for years {year_range[0]} to {year_range[1]} and countries {country_codes}.")
else:
    health_filtered = None

if economic_data is not None:
    economic_filtered = economic_data[
        (economic_data['Year'] >= year_range[0]) &
        (economic_data['Year'] <= year_range[1]) &
        (economic_data['iso_code'].isin(country_codes))
    ]
    economic_filtered = normalize_data(economic_filtered, ['value'])
    logger.debug(f"Economic data filtered for years {year_range[0]} to {year_range[1]} and countries {country_codes}.")
else:
    economic_filtered = None

if prediction_economic_data is not None:
    prediction_economic_filtered = prediction_economic_data[
        (prediction_economic_data['Year'] >= year_range[0]) &
        (prediction_economic_data['Year'] <= year_range[1]) &
        (prediction_economic_data['iso_code'].isin(country_codes))
    ]
    prediction_economic_filtered = normalize_data(prediction_economic_filtered, ['value'])
else:
    prediction_economic_filtered = None

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
                economic_indicator_name=economic_indicator_name,
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
                st.write(f"The correlation between **{health_indicator}** and **{economic_indicator_name}** is **{correlation:.2f}**.")
            else:
                st.subheader("🔗 Correlation Analysis")
                st.write("Insufficient data or variability to calculate correlation.")
        else:
            st.warning("Insufficient data to generate comparison chart.")

    elif chart_type == "Heatmap":
        if health_filtered is not None:
            plot_cross_country_heatmap(
                health_df=health_filtered,
                health_indicator=health_indicator
            )
        else:
            st.warning("Insufficient health data to generate heatmap.")

with col2:
    st.header("📈 Additional Insights")
    if health_filtered is not None and economic_filtered is not None:
        # Display Health Data
        st.subheader("🔍 Health Data Sample")
        st.dataframe(health_filtered.head())

        # Display Economic Data
        st.subheader("🔍 Economic Data Sample")
        st.dataframe(economic_filtered.head())

        # Download Options
        st.subheader("💾 Download Data")
        with st.expander("Download Health Data"):
            csv_health = health_filtered.to_csv(index=False)
            st.download_button(label="Download Health Data as CSV", data=csv_health, file_name='health_data.csv', mime='text/csv')

        with st.expander("Download Economic Data"):
            csv_economic = economic_filtered.to_csv(index=False)
            st.download_button(label="Download Economic Data as CSV", data=csv_economic, file_name='economic_data.csv', mime='text/csv')
    else:
        st.write("Data is insufficient to display additional insights.")

# ================== Machine Learning Integration ==================

# Option to train the model
if st.sidebar.button(f"Train {prediction_economic_indicator_name} Prediction Model"):
    if health_filtered is not None and prediction_economic_filtered is not None:
        with st.spinner(f"Training {prediction_economic_indicator_name} prediction model..."):
            rmse, r2 = train_economic_model(
                health_filtered,
                prediction_economic_filtered,
                target_col='value',
                indicator_code=prediction_economic_indicator_code
            )
            if rmse is not None and r2 is not None:
                st.sidebar.success(f"Model Trained Successfully!\nRMSE: {rmse:.2f}\nR²: {r2:.2f}")
            else:
                st.sidebar.error("Model training failed.")
    else:
        st.sidebar.error("Insufficient data to train the model.")

# Option to make predictions
st.sidebar.subheader(f"💡 Predict {prediction_economic_indicator_name}")
model = load_model(indicator_code=prediction_economic_indicator_code)
if model is not None:
    # Collect input features from the user
    st.sidebar.write("Enter Health Indicators for Prediction:")
    input_features = {}
    feature_columns = [
        'new_cases', 'new_deaths', 'total_cases', 'total_deaths',
        'new_cases_per_million', 'new_deaths_per_million',
        'reproduction_rate', 'icu_patients', 'hosp_patients',
        'population_density', 'median_age', 'aged_65_older',
        'aged_70_older', 'gdp_per_capita', 'cardiovasc_death_rate',
        'diabetes_prevalence', 'handwashing_facilities',
        'hospital_beds_per_thousand', 'life_expectancy',
        'human_development_index', 'extreme_poverty',
        'female_smokers', 'male_smokers'
    ]

    for feature in feature_columns:
        if feature in health_filtered.columns:
            input_features[feature] = st.sidebar.number_input(
                f"{feature.replace('_', ' ').title()}:",
                value=float(health_filtered[feature].mean())
            )
    
    if st.sidebar.button(f"Predict {prediction_economic_indicator_name}"):
        with st.spinner("Making prediction..."):
            prediction = predict_economic_indicator(model, list(input_features.values()))
            if prediction is not None:
                # Format the prediction based on the indicator type
                if "US$" in prediction_economic_indicator_name:
                    st.sidebar.success(f"Predicted {prediction_economic_indicator_name}: ${prediction:,.2f}")
                elif "%" in prediction_economic_indicator_name:
                    st.sidebar.success(f"Predicted {prediction_economic_indicator_name}: {prediction:.2f}%")
                else:
                    st.sidebar.success(f"Predicted {prediction_economic_indicator_name}: {prediction:,.2f}")
            else:
                st.sidebar.error("Prediction failed.")
else:
    st.sidebar.warning(f"No trained model found for {prediction_economic_indicator_name}. Please train the model first.")