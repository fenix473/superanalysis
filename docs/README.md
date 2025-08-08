# Data Analysis Project - Step-by-Step Analysis

## Overview
This project implements a step-by-step data analysis workflow, starting with importing data from a CSV file and performing NPS analysis.

## Step 1: CSV Data Import

### Purpose
Import data from the specified CSV file and convert it to a pandas DataFrame for analysis.

### Setup Instructions

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Ensure CSV File is Available
The script is configured to import from:
```
C:\Users\favil\Downloads\Working sheet - MERGED.csv
```

Make sure this file exists and is accessible.

### Usage

#### Run the Import Script
```bash
python python/step1_csv_import.py
```

#### Expected Output
The script will:
- Import data from CSV file
- Display basic information (rows, columns, first 5 rows)
- Save data to `csv/imported_data.csv` as backup

### Features
- **Simple Import**: Direct CSV file import
- **Basic Info Display**: Shows dataset dimensions and preview
- **Backup Export**: Automatically saves imported data to CSV

---

## Step 2: NPS Analysis

### Purpose
Calculate Net Promoter Score (NPS) per track and overall to measure program satisfaction.

### NPS Calculation
- **Promoters**: Scores 9-10 (likely to recommend)
- **Detractors**: Scores 0-6 (unlikely to recommend)
- **NPS Formula**: % Promoters - % Detractors

### Usage

#### Run the NPS Analysis
```bash
python python/step2_nps_analysis.py
```

### Results

#### Overall NPS: **59.3**

#### NPS by Track:
- **EXEC**: 71.4 (n=14) - *Executive Track*
- **PROD**: 55.6 (n=18) - *Productivity Track*  
- **DEV**: 54.5 (n=22) - *Developer Track*

### Key Insights:
- **Executive track** shows highest satisfaction (71.4 NPS)
- **Productivity and Developer tracks** have similar satisfaction levels (~55 NPS)
- **Overall program** performs well with a 59.3 NPS (considered "Good" range)

### Output Files
- `csv/nps_results.csv` - Detailed NPS scores for each track

---

### File Structure
```
Analysis/
├── python/step1_csv_import.py          # CSV import script
├── python/step2_nps_analysis.py        # NPS analysis script
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── csv/imported_data.csv           # Imported data backup
└── csv/nps_results.csv             # NPS analysis results
```

### Next Steps
After NPS analysis, the data is ready for deeper insights into session preferences, improvement areas, and track-specific feedback analysis.

---

**Note**: Each step builds on the previous one, creating a comprehensive analysis workflow.
