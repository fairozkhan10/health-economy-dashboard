# data_fetcher.py
# Author: Fairoz Khan
# Description: Module for fetching real-time health and economic data from APIs

import requests
import pandas as pd
import logging
import streamlit as st

def fetch_health_data():
    """Fetch COVID-19 health data from Our World in Data CSV dataset."""
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    try:
        logger.info("Attempting to fetch health data using pandas.")
        df = pd.read_csv(url, parse_dates=['date'])
        logger.info("Successfully fetched and parsed health data.")
        return df
    except Exception as e:
        logger.error(f"Error fetching health data: {e}")
        st.error(f"Error fetching health data: {e}")
        return None

def fetch_economic_data(country_codes, indicator_id):
    """Fetch economic data for multiple countries from the World Bank API."""
    try:
        logger.info(f"Fetching economic data for indicator '{indicator_id}' from World Bank API.")
        url = f"https://api.worldbank.org/v2/country/{';'.join(country_codes)}/indicator/{indicator_id}"
        params = {
            "format": "json",
            "per_page": "20000"  # Increase if needed
        }
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if len(data) == 2 and data[1]:
            records = data[1]
            df = pd.DataFrame.from_records(records)
            logger.info("Successfully fetched economic data.")
            return df
        else:
            logger.warning(f"No economic data found for indicator '{indicator_id}'.")
            st.warning(f"No economic data found for indicator '{indicator_id}'.")
            return None
    except Exception as e:
        logger.error(f"Error fetching economic data: {e}")
        st.error(f"Error fetching economic data: {e}")
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
    country_codes = ['USA', 'IND', 'BRA', 'CAN', 'GBR']
    indicator_id = "NY.GDP.MKTP.CD"  # GDP (Current US$)
    economic_data = fetch_economic_data(country_codes=country_codes, indicator_id=indicator_id)
    if economic_data is not None:
        logger.info("Economic Data Retrieved:")
        logger.info(economic_data.head())
    else:
        logger.error("Failed to retrieve economic data.")