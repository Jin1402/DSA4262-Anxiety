import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# 1. Load Cleaned Data
df_clean = pd.read_csv(r"C:\Users\asus\Downloads\cleaned_form_responses.csv")
df_clean = df_clean.loc[:, ~df_clean.columns.str.contains('^Unnamed')]

X = df_clean.drop(columns=["feas_total"])
y = df_clean["feas_total"]

# Add a constant (intercept) - Required for statsmodels GLM
X = sm.add_constant(X)

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Poisson GLM
# Family=Poisson() tells the model to treat the output as count data
poisson_model = sm.GLM(y_train, X_train, family=sm.families.Poisson()).fit()

# Print detailed statistical output (P-values)
print(poisson_model.summary())

# 4. Prediction and Testing
y_pred = poisson_model.predict(X_test)

print(f"\n--- Poisson Model Performance ---")
print(f"Mean Absolute Error: {mean_absolute_error(y_test, y_pred):.2f} points")
print(f"R-squared Score: {r2_score(y_test, y_pred):.2f}")

# 5. Visual Test: Actual vs. Predicted
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.6, color='seagreen')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
plt.title("Poisson Regression: Actual vs Predicted Stress")
plt.xlabel("Actual Score")
plt.ylabel("Predicted Score")
plt.grid(True)
plt.show()