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
   - Provides swimlane view with quarters as columns
   - Includes placeholder columns for:
     - Days in Quarter
     - Avg. Day Rate
     - Total Cost
     - Total Revenue

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

The notebook generates three CSV files:

- `Enhanced_Streamer_Projects.csv` - Original data with calculated duration columns
- `Quarterly_Breakdown.csv` - Project-level quarterly breakdown
- `Quarterly_Summary.csv` - Aggregated statistics by quarter

Note: Output CSV files are excluded from version control (see .gitignore)

## Data Source

The analysis uses data from: `Streamer Projects - SWG - AI.csv`
