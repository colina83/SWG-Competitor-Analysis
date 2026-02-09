# Recent Updates (February 2026)

## Changes Implemented

### 1. Dashboard Color Update
The Multi-Client project color in the Streamlit dashboard has been updated from bright green to dark green for better visibility and professional appearance.

**Before:** Bright Green (#00FF00)  
**After:** Dark Green (#006400)

See `color_change_comparison.png` for visual comparison.

### 2. Quarterly Breakdown Data
A new CSV file `quarterly_breakdown_data.csv` has been added containing the quarterly project breakdown with:
- Project name
- Vessel assignment
- Survey type
- Quarter (Q1-2025 through Q3-2025)

Total of 41 project entries across three quarters.

### 3. Dated CSV Files
The `generate_csv_files.py` script now generates CSV files with timestamps in the format `filename_YYYYMMDD.csv`. This helps track when the data was last generated while maintaining backward compatibility.

**Generated files:**
- `Enhanced_Streamer_Projects_YYYYMMDD.csv`
- `Vessel_Quarterly_Pivot_2025_YYYYMMDD.csv`
- `quarterly_breakdown_data_YYYYMMDD.csv`

**Note:** The non-dated versions are still created for backward compatibility with existing scripts.

## Usage

### Generate CSV Files with Dates
```bash
python generate_csv_files.py
```

This will create:
1. Dated versions (e.g., `Enhanced_Streamer_Projects_20260209.csv`)
2. Non-dated versions for backward compatibility

### Run Dashboard
```bash
streamlit run streamlit_dashboard.py
```

The dashboard will display Multi-Client projects in dark green.

### Access Quarterly Breakdown
The quarterly breakdown data is available in:
- `quarterly_breakdown_data.csv` (main file)
- `quarterly_breakdown_data_YYYYMMDD.csv` (dated copy)

## Files Modified
- `streamlit_dashboard.py` - Color update
- `generate_csv_files.py` - Added date stamping
- `.gitignore` - Exclude dated CSV files from git

## Files Created
- `quarterly_breakdown_data.csv` - Quarterly project breakdown
- `color_change_comparison.png` - Visual comparison of color change
- `CHANGES_SUMMARY.md` - Detailed change documentation
