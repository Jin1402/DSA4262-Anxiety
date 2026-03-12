import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# 1. Load the cleaned data
df_clean = pd.read_csv(r"C:\Users\asus\Downloads\cleaned_form_responses.csv")

# This drops any column that starts with 'Unnamed'
df_clean = df_clean.loc[:, ~df_clean.columns.str.contains('^Unnamed')]

# 2. Separate Features and Target
X = df_clean.drop(columns=["feas_total"])
y = df_clean["feas_total"]

# 3. Split into Training and Testing sets (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and Train the Regressor
# n_estimators=500 builds 500 trees for a very stable average
rf = RandomForestRegressor(n_estimators=500, random_state=42)
rf.fit(X_train, y_train)

# 5. Make Predictions
y_pred = rf.predict(X_test)

# 6. Evaluate Performance
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"--- Model Results ---")
print(f"Mean Absolute Error: {mae:.2f} points")
print(f"R-squared Score: {r2:.2f}")

# 7. Visualize Feature Importance
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
plt.title("Which behaviors drive anxiety (FEAS Total)?")
plt.bar(range(X.shape[1]), importances[indices])
plt.xticks(range(X.shape[1]), [X.columns[i] for i in indices], rotation=90)
plt.tight_layout()
plt.show()