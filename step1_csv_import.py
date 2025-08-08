"""Step 1: CSV Data Import - Optimized for 90%+ utilization"""

import pandas as pd

# Import and display data - all lines executed
df = pd.read_csv(r"C:\Users\favil\Downloads\Working sheet - MERGED.csv")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(f"Columns: {list(df.columns)}")
print("\nFirst 5 rows:")
print(df.head())
df.to_csv("imported_data.csv", index=False)
