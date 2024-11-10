# visualization.py
# Author: Fairoz Khan
# Description: Module for creating visualizations using Plotly and Matplotlib

import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

def plot_health_data(df, indicator, country_code):
    """Plot health data over time for a specific country using Plotly."""
    # Filter data for the specified country
    country_df = df[df['country_code'] == country_code]

    # Check if the indicator exists
    if indicator not in country_df.columns:
        st.write(f"Indicator '{indicator}' not found in the data.")
        return

    # Plot using Plotly
    fig = px.line(country_df, x='Year', y=indicator,
                  title=f'Health Data Over Time for {country_code}: {indicator}')
    st.plotly_chart(fig)

def plot_economic_data(df, indicator):
    """Plot economic data over time using Matplotlib."""
    # Check if the indicator exists
    if indicator not in df.columns:
        st.write(f"Indicator '{indicator}' not found in the data.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(df['Year'], df[indicator], label=indicator)
    plt.xlabel('Year')
    plt.ylabel(indicator)
    plt.title(f'{indicator} Over Time')
    plt.legend()
    st.pyplot(plt)
