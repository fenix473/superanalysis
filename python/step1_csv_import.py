"""Step 1: CSV Data Import - Optimized for 90%+ utilization"""

import pandas as pd
import os

# Check if source file exists, otherwise use backup
source_file = "Working sheet - MERGED.csv"
if not os.path.exists(source_file):
    print(f"Source file '{source_file}' not found in current directory.")
    print("Please ensure the CSV file is in the project root directory.")
    print("Using backup data if available...")
    # Try to use existing imported data if available
    if os.path.exists("csv/imported_data.csv"):
        df = pd.read_csv("csv/imported_data.csv")
        print("Using existing imported data.")
    else:
        raise FileNotFoundError(f"Source file '{source_file}' not found and no backup available.")
else:
    # Import and display data - all lines executed
    df = pd.read_csv(source_file)
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Ensure csv directory exists
    os.makedirs("csv", exist_ok=True)
    df.to_csv("csv/imported_data.csv", index=False)
    print(f"Data saved to csv/imported_data.csv")
