# visualization.py
# Author: Fairoz Khan
# Description: Module for creating visualizations of health and economic data


import matplotlib.pyplot as plt
import plotly.express as px


def plot_health_data(df, indicator = 'new_cases'):
    """Plot health data over time using Plotly."""
    fig = px.line(df, x = 'Year', y = indicator, title = 'Health Data Over Time')
    fig.show()


def plot_economic_data(df, indicator = 'value'):
    """Plot economic data over time using Matplotlib."""
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df[indicator], label=indicator)
    plt.xlabel('Year')
    plt.ylabel(indicator)
    plt.title(f'{indicator} Over Time')
    plt.legend()
    plt.grid()
    plt.show()




# Test Block
if __name__ == "__main__":
    import pandas as pd

    # Sample health data for testing
    health_data = pd.DataFrame({
        'Year': [2020, 2021, 2022],
        'new_cases': [1000, 5000, 3000]
    })
    print("Testing Health Data Plot...")
    plot_health_data(health_data, 'new_cases')

    # Sample economic data for testing
    economic_data = pd.DataFrame({
        'Year': [2020, 2021, 2022],
        'value': [2.5, 3.0, 3.5]
    }).set_index('Year')
    print("Testing Economic Data Plot...")
    plot_economic_data(economic_data, 'value')

