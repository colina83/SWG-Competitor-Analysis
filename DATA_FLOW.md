# Data Flow Documentation

## Overview

This document explains how data flows through the SWG Competitor Analysis system and how to update the data when the source file changes.

## Source File

**`Streamer Projects - SWG - AI.csv`** is the **primary source file** for all data transformations and calculations.

This file contains raw project data including:
- Survey Name
- Vessel assignments
- Project dates (Mobilisation Start, Deployment Start, Production Start, etc.)
- Day Rate
- Client information
- Country
- Activity type

## Data Flow Architecture

```
Streamer Projects - SWG - AI.csv (SOURCE)
                    ↓
          generate_csv_files.py
                    ↓
        ┌───────────┼───────────┐
        ↓           ↓           ↓
Enhanced_Streamer  Vessel_Q... quarterly_breakdown
_Projects.csv      uarterly_   _data.csv
                   Pivot_2025
                   .csv
        ↓           ↓           ↓
        └───────────┼───────────┘
                    ↓
          streamlit_dashboard.py
                    ↓
           Dashboard Display
```

## Generated Files

The following files are **automatically generated** from the source file:

1. **Enhanced_Streamer_Projects.csv**
   - Original data with calculated phase durations
   - Includes: Mobilization, Deployment, Production, Recovery, Demobilization, and Project Duration (all in days)

2. **Vessel_Quarterly_Pivot_2025.csv**
   - Vessel-aggregated data by quarter for 2025
   - Shows days worked, average day rate, total cost, and revenue per vessel per quarter
   - Wide format with Q1-Q4 columns

3. **quarterly_breakdown_data.csv**
   - Project-level quarterly breakdown
   - Shows which projects ran in which quarters
   - Includes vessel, survey type, and duration information

## How to Update Data

When the source file `Streamer Projects - SWG - AI.csv` is updated, you **MUST** regenerate all derived files.

### Method 1: Automated Update Script (Recommended)

```bash
./update_data.sh
```

This script will:
- Check that the source file exists
- Verify Python dependencies are installed
- Run the CSV generation process
- Provide clear success/error messages

### Method 2: Direct Python Script

```bash
python generate_csv_files.py
```

This script will:
1. Read from `Streamer Projects - SWG - AI.csv`
2. Calculate all phase durations
3. Generate quarterly breakdowns
4. Create vessel pivot tables
5. Save all output files with both dated and non-dated versions

### Output Files

The script creates two versions of each file:
- **Dated version** (e.g., `Enhanced_Streamer_Projects_20260210.csv`) - Timestamped for history
- **Non-dated version** (e.g., `Enhanced_Streamer_Projects.csv`) - For backward compatibility with the dashboard

## Dashboard Usage

The `streamlit_dashboard.py` reads from:
- `Streamer Projects - SWG - AI.csv` (for raw data)
- `Vessel_Quarterly_Pivot_2025.csv` (for pivot table)

The dashboard automatically loads the latest data when launched.

## Important Notes

⚠️ **Always regenerate derived files after updating the source file**

The pipeline ensures:
- No manual calculations are needed
- Consistent data across all views
- Proper handling of overlapping projects (no double-counting)
- Correct quarter boundaries and date calculations

## File Versioning

Old dated files are automatically removed when regenerating to keep the repository clean. Only the current date's files are kept.

## Dependencies

Required Python packages:
- pandas >= 2.0.0
- numpy >= 1.26.0
- streamlit >= 1.50.0 (for dashboard)
- plotly >= 5.0.0 (for dashboard)
- openpyxl >= 3.1.0

Install with:
```bash
pip install -r requirements.txt
```
