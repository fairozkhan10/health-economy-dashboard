# data_fetcher.py
# Author: Fairoz Khan
# Description: Module for fetching health and economic data from APIs. We'll use requests to pull data in JSON format


import requests
import pandas as pd


def fetch_health_data():
    """Fetch COVID-19 health data from Our World in Data."""
    url = "https://covid.ourworldindata.org/data/owid-covid-data.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data)   # Flatten JSON into a DataFrame
        return df
    else:
        print("Error fetching health data.")
        return None



def fetch_economic_data():
    """Fetch economic data from FRED (Federal Reserve Economic Data)."""

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "CPIAUCSL",  # Consumer Price Index for All Urban Consumers
        "api_key": "25ebb6a3f76de7b2e9922fc688c0210a",  # Replace with your FRED API key
        "file_type": "json"
    }
    response = requests.get(url, params)

    if response.status_code == 200:
        data = response.json()
        observations = data['observations']
        df = pd.json_normalize(observations)
        return df
    else:
        print("Error fetching economic data.")
        return None
    


# Test Block
if __name__ == "__main__":
    print("Testing Health Data Fetching...")
    health_data = fetch_health_data()
    if health_data is not None:
        print("Health Data Retrieved:")
        print(health_data.head())

    print("\nTesting Economic Data Fetching...")
    economic_data = fetch_economic_data()
    if economic_data is not None:
        print("Economic Data Retrieved:")
        print(economic_data.head())