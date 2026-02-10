# SWG Competitor Analysis

This repository contains analysis tools for Shearwater competitor project data.

## Quick Start

After updating the source file `Streamer Projects - SWG - AI.csv`, always run:

```bash
python generate_csv_files.py
```

This regenerates all derived files (pivot tables, quarterly breakdowns) from the source data.

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

## CSV File Generator

The repository includes a standalone Python script for generating CSV files: `generate_csv_files.py`

### Purpose

This script reads the source data file and generates all required CSV files for the dashboard without needing Jupyter. It is based on the Jupyter notebook logic but optimized for automation.

### Usage

```bash
python generate_csv_files.py
```

### What it does

1. Reads from `Streamer Projects - SWG - AI.csv`
2. Calculates all phase durations (Mobilization, Deployment, Production, etc.)
3. Generates `Enhanced_Streamer_Projects.csv` with duration columns
4. Creates vessel quarterly pivot table for 2025
5. Generates quarterly breakdown data with proper handling of overlapping projects
6. Creates both dated versions (with timestamp) and non-dated versions (for backward compatibility)
7. Automatically removes old dated files

### Output Files

The script generates:
- `Enhanced_Streamer_Projects.csv` / `Enhanced_Streamer_Projects_YYYYMMDD.csv`
- `Vessel_Quarterly_Pivot_2025.csv` / `Vessel_Quarterly_Pivot_2025_YYYYMMDD.csv`
- `quarterly_breakdown_data.csv` / `quarterly_breakdown_data_YYYYMMDD.csv`

## Data Source

**Primary Source File:** `Streamer Projects - SWG - AI.csv`

This is the **single source of truth** for all data transformations and calculations.

### Updating Data

When the source file is updated, you **must** regenerate the derived files:

```bash
python generate_csv_files.py
```

This ensures all pivot tables and quarterly breakdowns are synchronized with the latest source data.

For detailed information about the data flow, see [DATA_FLOW.md](DATA_FLOW.md).

---

## Streamlit Dashboard

The repository now includes an interactive Streamlit dashboard for visualizing the 2025 vessel project timeline.

### Features

The dashboard provides:

1. **Interactive Gantt-style Timeline Chart:**
   - Displays all vessels (11 total, including Island Pride (Charter))
   - Shows project phases with color coding:
     - Mobilization: Yellow
     - Deployment: Orange
     - Production: Green
     - Recovery: Orange
     - Demobilization: Yellow
   - Months displayed on X-axis (at the top)
   - Quarters marked with vertical lines and labels
   - Legend format: Country + Type of Survey (e.g., "India 2D")
   - Interactive hover tooltips with project details

2. **Vessel Quarterly Pivot Table:**
   - Summary of vessel utilization by quarter (Q1-Q4 2025)
   - Days worked per quarter
   - Average day rate
   - Total cost per quarter
   - Revenue column removed as requested

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas openpyxl streamlit plotly
```

### Running the Dashboard

1. Ensure the data file `Streamer Projects - SWG - AI.csv` is in the repository root

2. Generate the processed data files by running the notebook (or the CSV files should already exist):
   ```bash
   # If you need to regenerate data files
   jupyter notebook "Shearwater Competitor Information.ipynb"
   # Run all cells in the notebook
   ```

3. Launch the Streamlit dashboard:
   ```bash
   streamlit run streamlit_dashboard.py
   ```

4. The dashboard will open in your default web browser at `http://localhost:8501`

5. To stop the dashboard, press `Ctrl+C` in the terminal

### Dashboard Files

- `streamlit_dashboard.py` - Main dashboard application
- `Enhanced_Streamer_Projects.csv` - Processed project data with calculated durations
- `Vessel_Quarterly_Pivot_2025.csv` - Vessel quarterly summary data

### Usage Tips

- Hover over any bar in the timeline to see detailed project information
- The timeline shows the entire 2025 calendar year with quarters clearly marked
- The table at the bottom can be scrolled and sorted as needed
- The dashboard automatically updates if you regenerate the data files
