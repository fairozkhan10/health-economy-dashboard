# data_fetcher.py
# Author: Fairoz Khan
# Description: Module for fetching real-time health and economic data from APIs

import requests
import pandas as pd

def fetch_health_data():
    """Fetch COVID-19 health data for multiple countries from Our World in Data."""
    url = "https://covid.ourworldindata.org/data/owid-covid-data.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame.from_dict(data, orient='index').reset_index()
        df.rename(columns={"index": "country_code"}, inplace=True)
        return df
    else:
        print("Error fetching health data.")
        return None

def fetch_economic_data(series_ids=["CPIAUCSL"]):
    """Fetch multiple economic data series from FRED for the US."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    api_key = "489851a631691e5e8cfe3f5fa17ea484"  # Replace with your actual FRED API key

    all_series_data = []
    for series_id in series_ids:
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json"
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            observations = data.get("observations", [])
            if observations:
                df = pd.json_normalize(observations)
                df["series_id"] = series_id
                all_series_data.append(df)
        else:
            print(f"Error fetching economic data for series_id {series_id}: {response.text}")

    if all_series_data:
        df_combined = pd.concat(all_series_data, ignore_index=True)
        return df_combined
    else:
        return None

# Test Block
if __name__ == "__main__":
    # Testing Health Data Fetching
    print("Testing Health Data Fetching...")
    health_data = fetch_health_data()
    if health_data is not None:
        print("Health Data Retrieved:")
        print(health_data.head())
    else:
        print("Failed to retrieve health data.")

    # Testing Economic Data Fetching
    print("\nTesting Economic Data Fetching...")
    economic_data = fetch_economic_data(series_ids=["CPIAUCSL", "GDP"])
    if economic_data is not None:
        print("Economic Data Retrieved:")
        print(economic_data.head())
    else:
        print("Failed to retrieve economic data.")
