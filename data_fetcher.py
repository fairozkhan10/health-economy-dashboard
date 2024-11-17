# data_fetcher.py
# Author: Fairoz Khan
# Description: Module for fetching real-time health and economic data from APIs

import os
import requests
import pandas as pd
import logging
import streamlit as st  # Import Streamlit to access secrets


def fetch_health_data():
    """Fetch COVID-19 health data for multiple countries from Our World in Data."""
    url = "https://covid.ourworldindata.org/data/owid-covid-data.json"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        df.rename(columns={"index": "country_code"}, inplace=True)
        logger.info("Successfully fetched health data.")
        return df
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching health data: {e}")
        st.error(f"Error fetching health data: {e}")
        return None


def fetch_economic_data(series_ids=["CPIAUCSL"]):
    """Fetch multiple economic data series from FRED."""
    url = "https://api.stlouisfed.org/fred/series/observations"

    # Fetch API key from Streamlit secrets first, fallback to environment variable
    api_key = st.secrets["FRED_API_KEY"] if "FRED_API_KEY" in st.secrets else os.getenv("FRED_API_KEY")

    if not api_key:
        logger.error("FRED_API_KEY not set in Streamlit secrets or environment variables.")
        st.error("Error: FRED_API_KEY not set in Streamlit secrets or environment variables.")
        return None

    all_series_data = []
    for series_id in series_ids:
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json"
        }
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            observations = data.get("observations", [])
            if observations:
                df = pd.json_normalize(observations)
                df["series_id"] = series_id
                all_series_data.append(df)
                logger.info(f"Successfully fetched economic data for series_id {series_id}.")
            else:
                logger.warning(f"No observations found for series_id {series_id}.")
                st.warning(f"No observations found for series_id {series_id}.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching economic data for series_id {series_id}: {e}")
            st.error(f"Error fetching economic data for series_id {series_id}: {e}")

    if all_series_data:
        combined_df = pd.concat(all_series_data, ignore_index=True)
        logger.info("Successfully combined all economic data.")
        return combined_df
    else:
        logger.error("No economic data fetched.")
        st.error("No economic data fetched.")
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

# Test Block
if __name__ == "__main__":
    # Testing Health Data Fetching
    logger.info("Testing Health Data Fetching...")
    health_data = fetch_health_data()
    if health_data is not None:
        logger.info("Health Data Retrieved:")
        logger.info(health_data.head())
    else:
        logger.error("Failed to retrieve health data.")

    # Testing Economic Data Fetching
    logger.info("\nTesting Economic Data Fetching...")
    economic_data = fetch_economic_data(series_ids=["CPIAUCSL", "GDP"])
    if economic_data is not None:
        logger.info("Economic Data Retrieved:")
        logger.info(economic_data.head())
    else:
        logger.error("Failed to retrieve economic data.")
