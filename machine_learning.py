# machine_learning.py
# Author: Fairoz Khan
# Description: Module for implementing machine learning models for predictive analysis

import pandas as pd
import logging
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def train_economic_model(health_df, economic_df, target_col='value', indicator_code='indicator'):
    """Train a Linear Regression model to predict an economic indicator based on health indicators."""
    try:
        logger.info(f"Starting training of {indicator_code} prediction model.")
        
        # Merge health and economic data on 'iso_code' and 'Year'
        merged_df = pd.merge(
            health_df,
            economic_df,
            on=['iso_code', 'Year'],
            how='inner',
            suffixes=('_health', '_econ')
        )
        logger.debug(f"Merged data for modeling:\n{merged_df.head()}")
        
        # Define features and target
        feature_cols = [
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
        
        # Ensure all feature columns are present
        feature_cols = [col for col in feature_cols if col in merged_df.columns]
        
        X = merged_df[feature_cols]
        y = merged_df[target_col]
        
        # Handle missing values
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        logger.info(f"Training data shape: {X_train.shape}, Testing data shape: {X_test.shape}")
        
        # Initialize and train the model
        model = LinearRegression()
        model.fit(X_train, y_train)
        logger.info("Model training completed.")
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Evaluate the model
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        r2 = r2_score(y_test, y_pred)
        logger.info(f"Model Evaluation - RMSE: {rmse}, R²: {r2}")
        
        # Save the model with a dynamic filename
        model_filename = f"{indicator_code}_prediction_model.joblib"
        joblib.dump(model, model_filename)
        logger.info(f"Model saved as '{model_filename}'.")
        
        return rmse, r2
    except Exception as e:
        logger.error(f"Error training {indicator_code} model: {e}")
        st.error(f"Error training {indicator_code} model: {e}")
        return None, None

def predict_economic_indicator(model, input_data):
    """Use the trained model to predict the economic indicator based on input data."""
    try:
        prediction = model.predict([input_data])[0]
        logger.info(f"Predicted economic indicator: {prediction}")
        return prediction
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        st.error(f"Error making prediction: {e}")
        return None

def load_model(indicator_code='indicator'):
    """Load the trained prediction model for the specified economic indicator."""
    try:
        model_filename = f"{indicator_code}_prediction_model.joblib"
        model = joblib.load(model_filename)
        logger.info(f"Model '{model_filename}' loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Error loading model '{model_filename}': {e}")
        st.error(f"Error loading model '{model_filename}': {e}")
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
