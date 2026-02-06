# Streamlit Dashboard Quick Start Guide

This guide will help you run the Shearwater Competitor Analysis Dashboard.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Required Dependencies

Open a terminal/command prompt and navigate to the project directory, then run:

```bash
pip install -r requirements.txt
```

This will install:
- pandas (data processing)
- openpyxl (Excel file support)
- streamlit (web dashboard framework)
- plotly (interactive charts)

### 2. Verify Data Files

Ensure the following files are present in the project directory:
- `Streamer Projects - SWG - AI.csv` (source data)
- `Enhanced_Streamer_Projects.csv` (generated from notebook)
- `Vessel_Quarterly_Pivot_2025.csv` (generated from notebook)

If the CSV files are missing, run the Jupyter notebook first:
```bash
jupyter notebook "Shearwater Competitor Information.ipynb"
```
Then run all cells to generate the required data files.

## Running the Dashboard

### Start the Dashboard

In your terminal, run:

```bash
streamlit run streamlit_dashboard.py
```

### Access the Dashboard

The dashboard will automatically open in your default web browser at:
```
http://localhost:8501
```

If it doesn't open automatically, manually navigate to the URL shown in the terminal.

### Stop the Dashboard

To stop the dashboard, press `Ctrl+C` in the terminal where Streamlit is running.

## Dashboard Features

### 1. **Interactive Timeline Chart**
- Shows all 11 vessels (including Island Pride (Charter))
- Color-coded project phases:
  - **Yellow**: Mobilization & Demobilization
  - **Orange**: Deployment & Recovery
  - **Green**: Production
  - **Light Gray**: Transit time (gaps between projects)
- Months displayed on top X-axis
- Quarters marked with vertical dashed lines
- Hover over bars to see project details

### 2. **Vessel Quarterly Pivot Table**
- Summary of vessel utilization by quarter (Q1-Q4 2025)
- Shows days worked, average day rate, and total cost per quarter
- Scrollable and sortable

## Troubleshooting

### Port Already in Use

If you get an error that port 8501 is already in use, you can specify a different port:

```bash
streamlit run streamlit_dashboard.py --server.port 8502
```

Then access the dashboard at `http://localhost:8502`

### Missing Data Files

If you see errors about missing CSV files, make sure you've run the Jupyter notebook to generate the data files first.

### Module Not Found Errors

If you get "ModuleNotFoundError", make sure you've installed all dependencies:

```bash
pip install -r requirements.txt
```

## Updating the Data

To update the dashboard with new data:

1. Update `Streamer Projects - SWG - AI.csv` with new project information
2. Run the Jupyter notebook to regenerate the processed CSV files
3. Refresh the dashboard in your browser (Streamlit will automatically detect file changes)

## Need Help?

For more information about Streamlit, visit: https://docs.streamlit.io/
