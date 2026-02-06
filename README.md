# SWG Competitor Analysis

This repository contains analysis tools for Shearwater competitor project data.

## Shearwater Competitor Information Notebook

The main analysis is performed in the Jupyter Notebook: `Shearwater Competitor Information.ipynb`

### Features

The notebook analyzes streamer project data and calculates:

1. **Project Phase Durations:**
   - Mobilization (days) = Deployment Start – Mobilization Start
   - Deployment (days) = Production Start – Deployment Start
   - Production (days) = Production End – Production Start
   - Recovery (days) = Retrieval End – Production End
   - Demobilization (days) = Demobilization End – Retrieval End
   - Project Duration = Demobilization End – Mobilization Start

2. **Quarterly Breakdown:**
   - Calculates days spent per quarter for each project
   - Includes vessel and survey type information for each project
   - Provides swimlane view with quarters as columns
   - Includes columns for:
     - Project name
     - Vessel
     - Survey Type
     - Quarter
     - Days in Quarter
     - Avg. Day Rate
     - Total Cost
     - Total Revenue

3. **Vessel Quarterly Aggregation (2025 only):**
   - Aggregates project data by vessel and quarter
   - Excludes Q4 2024 and Q1 2026 data
   - Calculates for each vessel and quarter:
     - Number of days the vessel spent on projects
     - Average day rate (weighted by days)
     - Total cost for the quarter
     - Total revenue for the quarter
   - Available in both long and wide (pivot) formats

### Installation

Install required dependencies:

```bash
pip install -r dependencies.txt
```

Or install individually:
```bash
pip install jupyter pandas openpyxl matplotlib seaborn
```

### Usage

1. Ensure the data file `Streamer Projects - SWG - AI.csv` is in the repository root
2. Launch Jupyter:
   ```bash
   jupyter notebook
   ```
3. Open `Shearwater Competitor Information.ipynb`
4. Run all cells (Kernel → Restart & Run All)

### Output Files

The notebook generates one Excel file and multiple CSV files:

**Primary Output:**
- `Quarterly_Review_Breakdown.xlsx` - Main Excel workbook containing:
  - **Quarterly Breakdown** - Project-level quarterly breakdown with vessel and survey type
  - **Quarterly Summary** - Aggregated statistics by quarter
  - **Vessel Quarterly 2025** - Vessel-aggregated data by quarter (long format)
  - **Vessel Quarterly Pivot 2025** - Vessel-aggregated data by quarter (wide format)

**CSV Exports (for backward compatibility):**
- `Enhanced_Streamer_Projects.csv` - Original data with calculated duration columns
- `Quarterly_Breakdown.csv` - Project-level quarterly breakdown
- `Quarterly_Summary.csv` - Aggregated statistics by quarter
- `Vessel_Quarterly_2025.csv` - Vessel quarterly data (long format)
- `Vessel_Quarterly_Pivot_2025.csv` - Vessel quarterly data (wide format)

Note: CSV output files are excluded from version control (see .gitignore). The Excel file is tracked for sharing.

## Data Source

The analysis uses data from: `Streamer Projects - SWG - AI.csv`
