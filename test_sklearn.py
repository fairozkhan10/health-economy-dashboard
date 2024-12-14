# test_sklearn.py

from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import numpy as np
import inspect

# Test mean_squared_error with 'squared' parameter
y_true = [3, -0.5, 2, 7]
y_pred = [2.5, 0.0, 2, 8]

try:
    mse = mean_squared_error(y_true, y_pred, squared=False)
    print(f"RMSE: {mse}")
except Exception as e:
    print(f"Error: {e}")

# Verify the signature of mean_squared_error
print(f"mean_squared_error signature: {inspect.signature(mean_squared_error)}")
