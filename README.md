# Health and Economy Dashboard

## Overview

The **Health and Economy Dashboard** is an interactive web application that integrates and visualizes comprehensive health and economic data from over 30 countries. Leveraging Python, Streamlit, and Plotly, the dashboard offers real-time analysis of key indicators such as COVID-19 cases and GDP growth. Additionally, it incorporates machine learning functionalities to predict GDP based on health metrics.

## Features

- **Data Integration:** Combines health data from Our World in Data and economic data from the World Bank API.
- **Interactive Visualizations:** Compare health and economic indicators across countries and years using dynamic charts and heatmaps.
- **Correlation Analysis:** Explore the relationships between different health and economic metrics.
- **Predictive Modeling:** Train and utilize a Linear Regression model to forecast GDP based on selected health indicators.
- **User-Friendly Interface:** Customize country selections, indicators, and year ranges to tailor the analysis.
- **Data Download:** Export filtered datasets for further analysis.

## Setup Instructions

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/health-economy-dashboard.git
    cd health-economy-dashboard
    ```

2. **Set Up a Conda Environment:**

    ```bash
    conda create -n health-econ-dashboard python=3.9
    conda activate health-econ-dashboard
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Application:**

    ```bash
    streamlit run app.py
    ```

5. **Access the Dashboard:**

    Open your browser and navigate to [http://localhost:8501](http://localhost:8501).

## Usage Guidelines

1. **Select Countries:** Use the sidebar to choose one or multiple countries for analysis.

2. **Choose Indicators:** Select desired health and economic indicators from the provided options.

3. **Customize Year Range:** Adjust the slider to define the time frame for the data analysis.

4. **Visualize Data:** 
    - **Comparison Chart:** Compare health and economic indicators across selected countries and years.
    - **Heatmap:** Visualize the distribution of a specific health indicator across countries and years.

5. **Correlation Analysis:** View the correlation coefficient between selected health and economic metrics.

6. **Predict GDP:**
    - **Train Model:** Click on the "Train GDP Prediction Model" button to train the Linear Regression model using the currently filtered data.
    - **Make Predictions:** Input specific health metrics to forecast GDP values.

7. **Download Data:** Export the filtered health and economic datasets as CSV files for offline analysis.

## Project Structure

health-economy-dashboard/
├── data/
│   ├── health_data.csv  # Example data storage
│   ├── economic_data.csv  # Example economic data storage
├── app.py  # Main Streamlit application
├── requirements.txt  # Python dependencies
├── README.md  # Project documentation
├── machine_learning.py  # ML model implementations
├── visualization.py  # Visualization utilities
├── data_processing.py  # Data cleaning and transformation
├── data_fetcher.py  # API integration for data fetching
└── tests/  # Unit tests for core functionalities



## Future Enhancements

- **Advanced Machine Learning Models:** Incorporate more sophisticated models like Random Forest or Gradient Boosting for improved prediction accuracy.
- **Clustering:** Group countries based on similarities in health and economic metrics using clustering algorithms.
- **Anomaly Detection:** Identify outliers in the data to highlight unusual trends or events.
- **Enhanced Visualizations:** Implement additional interactive charts and dashboards for deeper insights.
- **Real-Time Updates:** Automate periodic data refresh to ensure up-to-date analysis.


## Contact

For any queries or suggestions, feel free to contact me at:
- **Email:** [fkhan35@wisc.edu] or [saify2001@icloud.com]
