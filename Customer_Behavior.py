# CUSTOMER SHOPPING BEHAVIOR
# -------------------------
# Data cleaning and loading pipeline
# Reads the customer shopping dataset, cleans the data,
# creates useful columns, and loads the final data into PostgreSQL.

import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("customer_shopping_behavior.csv")

print("First 5 Rows:")
print(df.head())

print("\nDataset Information:")
print(df.info())

print("\nDataset Description:")
print(df.describe(include="all"))

print("\nMissing Values:")
print(df.isnull().sum())


# ============================================================
# 2. HANDLE MISSING VALUES
# ============================================================

# Fill missing Review Rating values using the median
# of the corresponding product category.
df["Review Rating"] = (
    df.groupby("Category")["Review Rating"]
    .transform(lambda x: x.fillna(x.median()))
)

print("\nMissing Values After Cleaning:")
print(df.isnull().sum())


# ============================================================
# 3. CLEAN COLUMN NAMES
# ============================================================

# Convert all column names to lowercase.
df.columns = df.columns.str.lower()

# Replace spaces with underscores.
df.columns = df.columns.str.replace(" ", "_")

print("\nColumn Names After Snake Case:")
print(df.columns)


# Rename purchase_amount_(usd) to purchase_amount.
df = df.rename(
    columns={
        "purchase_amount_(usd)": "purchase_amount"
    }
)

print("\nFinal Column Names:")
print(df.columns)


# ============================================================
# 4. CREATE AGE GROUP
# ============================================================

# Divide customers into four age groups based on age quartiles.
label = [
    "Young Adult",
    "Adult",
    "Middle Age",
    "Senior"
]

df["age_group"] = pd.qcut(
    df["age"],
    q=4,
    labels=label
)

print("\nAge Groups:")
print(df[["age", "age_group"]].head(10))


# ============================================================
# 5. CREATE PURCHASE FREQUENCY IN DAYS
# ============================================================

# Convert purchase frequency into an approximate
# number of days between purchases.
freq_map = {
    "Fortnightly": 14,
    "Weekly": 7,
    "Monthly": 30,
    "Quarterly": 90,
    "Bi-Weekly": 14,
    "Annually": 365,
    "Every 3 Months": 90
}

df["purchase_frequency_days"] = (
    df["frequency_of_purchases"].map(freq_map)
)

print("\nPurchase Frequency:")
print(
    df[
        [
            "purchase_frequency_days",
            "frequency_of_purchases"
        ]
    ].head(10)
)


# ============================================================
# 6. REMOVE DUPLICATE INFORMATION
# ============================================================

# Check whether discount_applied and promo_code_used
# contain the same information.
print("\nDiscount and Promo Code Check:")
print(
    df[
        [
            "discount_applied",
            "promo_code_used"
        ]
    ].head(10)
)

print(
    "\nAre both columns identical?",
    (df["discount_applied"] == df["promo_code_used"]).all()
)

# Remove promo_code_used because it duplicates discount_applied.
df = df.drop(
    "promo_code_used",
    axis=1
)

print("\nColumns After Removing Duplicate Column:")
print(df.columns)


# ============================================================
# 7. CONNECT TO POSTGRESQL
# ============================================================

# Keep database credentials outside the GitHub repository.
# Replace these values locally or use environment variables.
username = "postgres"
password = "PostgreSQL@2026"
host = "localhost"
port = "5432"
database = "Project"

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{username}:{quote_plus(password)}"
    f"@{host}:{port}/{database}"
)


# ============================================================
# 8. LOAD DATA INTO POSTGRESQL
# ============================================================

table_name = "customer"

df.to_sql(
    table_name,
    engine,
    if_exists="replace",
    index=False
)

print(
    f"\nData successfully loaded into table "
    f"'{table_name}' in database '{database}'."
)
