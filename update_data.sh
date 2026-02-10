#!/bin/bash
# Script to update all derived data files after updating the source CSV
# Usage: ./update_data.sh

set -e  # Exit on error

echo "=================================================="
echo "SWG Competitor Analysis - Data Update Script"
echo "=================================================="
echo ""

# Check if source file exists
if [ ! -f "Streamer Projects - SWG - AI.csv" ]; then
    echo "❌ ERROR: Source file 'Streamer Projects - SWG - AI.csv' not found!"
    echo "   Please ensure the file exists in the current directory."
    exit 1
fi

echo "✓ Source file found: Streamer Projects - SWG - AI.csv"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed!"
    exit 1
fi

echo "✓ Python 3 is available"
echo ""

# Check if required packages are installed
echo "Checking Python dependencies..."
python3 -c "import pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Required Python packages not found. Installing..."
    pip install -r requirements.txt
    echo ""
fi

echo "✓ Python dependencies are installed"
echo ""

# Run the generator script
echo "Regenerating CSV files from source data..."
echo ""
python3 generate_csv_files.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ SUCCESS! All data files have been updated."
    echo "=================================================="
    echo ""
    echo "Generated files:"
    echo "  - Enhanced_Streamer_Projects.csv"
    echo "  - Vessel_Quarterly_Pivot_2025.csv"
    echo "  - quarterly_breakdown_data.csv"
    echo ""
    echo "You can now run the dashboard with:"
    echo "  streamlit run streamlit_dashboard.py"
    echo ""
else
    echo ""
    echo "❌ ERROR: Failed to generate CSV files!"
    exit 1
fi
