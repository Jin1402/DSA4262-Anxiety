import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Load data
df = pd.read_excel(r"C:\Users\asus\Downloads\form_responses.xlsx")

# --- Calculate feas_total from survey items ---
'''
feas_items = [
    "feas_pa1","feas_pa2","feas_pa3","feas_pa4","feas_pa5",
    "feas_ka1","feas_ka2","feas_ka3","feas_ka4",
    "feas_cr1","feas_cr2","feas_cr3","feas_cr4",
    "feas_sr1","feas_sr2","feas_sr3","feas_sr4"
]

# Convert to numeric (in case Excel stored them as text)
df[feas_items] = df[feas_items].apply(pd.to_numeric, errors="coerce")

# Calculate total score
df["feas_total"] = df[feas_items].sum(axis=1)

# Drop the original columns
df = df.drop(columns=feas_items + ["ac1", "ac2", "bhv_job_search_exp", "consent", "timestamp"])
'''

# Target
y = df["feas_total"]
X = df.drop(columns=["feas_total"])

# Columns with natural order
ordinal_cols = [
    "demo_honours_class",
    "demo_job_search_status",
    "demo_num_prior_interns",
    "bhv_apps_4_wks",
    "bhv_itvs_4_wks",
    "bhv_job_update_check_daily",
    "bhv_app_duration",
    "bhv_app_status_check_daily",
    "bhv_app_avoidance_weekly"
]

# Convert ordinal columns to string
X[ordinal_cols] = X[ordinal_cols].astype(str)

# Define the correct order
ordinal_categories = [
    ["Pass", "Honours", "Honours (Merit)", "Honours (Distinction)", "Honours (Highest Distinction)"],
    ["Not started", "Planning to apply soon", "Actively applying", "Secured but still actively applying", "Already secured job"],
    ["0", "1-2", "3 and above"],
    ["0", "1-5", "5-15", "16 - 30", "31+"],
    ["0", "1", "2-3", "4+"],
    ["0", "1-2", "3-5", "6+"],
    ["Not Applicable", "<10 min", "10 - 30 min", "30 - 60 min", "1 - 2 h", "> 2h"],
    ["Not Applicable", "0", "1-2", "3-5", "6 +"],
    ["0", "1-2", "3-5", "6 +"]
]

# Columns with no order
nominal_cols = ["demo_gender", "demo_area_of_study"]

ordinal_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OrdinalEncoder(categories=ordinal_categories))
])

nominal_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("ord", ordinal_pipeline, ordinal_cols),
        ("nom", nominal_pipeline, nominal_cols)
    ],
    remainder="passthrough"
)

# Transform features
X_processed = preprocessor.fit_transform(X)

print(X_processed[:5])

# Get new column names
feature_names = preprocessor.get_feature_names_out()

# Convert to DataFrame
clean_df = pd.DataFrame(X_processed, columns=feature_names)

# Add target back
clean_df["feas_total"] = y.values

# save cleaned dataset
#clean_df.to_csv("data/cleaned_form_responses.csv", index=False)
clean_df.to_csv(r"C:\Users\asus\Downloads\cleaned_form_responses.csv")
