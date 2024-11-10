# data_processing.py
# Author: Fairoz Khan
# Description: Module for cleaning and transforming data


import pandas as pd

def clean_data(df):
    """Clean data by removing NaN values and duplicates."""
    df = df.dropna().drop_duplicates()
    return df

def transform_data(df, date_column):
    """Transform data by extracting year and aggregating by year."""
    df[date_column] = pd.to_datetime(df[date_column])
    df['Year'] = df[date_column].dt.year
    df_grouped = df.groupby('Year').mean()
    return df_grouped

# Test Block
if __name__ == "__main__":
    # Sample data
    data = {
        'date': ['2022-01-01', '2022-02-01', '2023-01-01', '2023-02-01', None],
        'value': [10, 20, None, 40, 50]
    }
    df = pd.DataFrame(data)

    print("Original Data:")
    print(df)

    # Clean data
    cleaned_df = clean_data(df)
    print("\nCleaned Data:")
    print(cleaned_df)

    # Transform data
    transformed_df = transform_data(cleaned_df, 'date')
    print("\nTransformed Data:")
    print(transformed_df)
