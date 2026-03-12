import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# 1. Load and Clean Data
path = r"C:\Users\asus\Downloads\cleaned_form_responses.csv"
df_clean = pd.read_csv(path)

# Remove the unnamed index column if it exists
df_clean = df_clean.loc[:, ~df_clean.columns.str.contains('^Unnamed')]

# Define Features (X) and Target (y)
X = df_clean.drop(columns=["feas_total"])
y = df_clean["feas_total"]

# 2. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Initialize and Train Random Forest
rf = RandomForestRegressor(n_estimators=500, max_depth=10, random_state=42)
rf.fit(X_train, y_train)

# 4. Predictions and Performance Metrics
y_pred = rf.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
residuals = y_test - y_pred

print(f"--- Model Performance ---")
print(f"Mean Absolute Error (MAE): {mae:.2f} points")
print(f"R-squared (Accuracy): {r2:.2f}")
print(f"Relative Error: {(mae / (85-17)) * 100:.2f}% of scale range")

# --- VISUALIZATIONS ---

# Setup a 2x2 grid for plots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Feature Importance (Which behaviors matter most?)
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]
sns.barplot(x=importances[indices][:10], y=X.columns[indices][:10], ax=axes[0, 0], palette="viridis")
axes[0, 0].set_title("Top 10 Predictors of Anxiety")

# Plot 2: Distribution of Scores (Test A: Ceiling/Floor Effects)
sns.histplot(y, kde=True, bins=20, color='teal', ax=axes[0, 1])
axes[0, 1].axvline(17, color='red', linestyle='--', label='Min (17)')
axes[0, 1].axvline(85, color='red', linestyle='--', label='Max (85)')
axes[0, 1].set_title("Distribution of Actual Anxiety Scores")
axes[0, 1].legend()

# Plot 3: Residual Plot (Test B: Homoscedasticity)
axes[1, 0].scatter(y_pred, residuals, alpha=0.5, color='purple')
axes[1, 0].axhline(0, color='black', linestyle='--')
axes[1, 0].set_title("Residual Plot (Error Consistency)")
axes[1, 0].set_xlabel("Predicted Score")
axes[1, 0].set_ylabel("Error")

# Plot 4: Actual vs. Predicted (Visual Accuracy)
axes[1, 1].scatter(y_test, y_pred, alpha=0.5)
axes[1, 1].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
axes[1, 1].set_title("Actual vs. Predicted Scores")
axes[1, 1].set_xlabel("Actual")
axes[1, 1].set_ylabel("Predicted")

plt.tight_layout()

plt.show()
