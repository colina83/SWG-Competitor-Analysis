#!/usr/bin/env python3
"""
Validation script to ensure data consistency across all files.
This script verifies that all derived files are properly synchronized with the source file.
"""

import pandas as pd
import sys
from datetime import datetime

def validate_data_flow():
    """Validate that all derived files are consistent with the source."""
    
    print("=" * 60)
    print("Data Flow Validation")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # Check 1: Source file exists
    print("1. Checking source file...")
    try:
        source_df = pd.read_csv("Streamer Projects - SWG - AI.csv")
        print(f"   ✓ Source file loaded: {len(source_df)} projects")
    except FileNotFoundError:
        errors.append("Source file 'Streamer Projects - SWG - AI.csv' not found")
        print("   ❌ Source file not found!")
        return errors, warnings
    
    # Check 2: Enhanced file exists and has same number of rows
    print("2. Checking Enhanced_Streamer_Projects.csv...")
    try:
        enhanced_df = pd.read_csv("Enhanced_Streamer_Projects.csv")
        if len(enhanced_df) != len(source_df):
            errors.append(f"Enhanced file has {len(enhanced_df)} rows, source has {len(source_df)}")
            print(f"   ❌ Row count mismatch!")
        else:
            print(f"   ✓ Enhanced file loaded: {len(enhanced_df)} projects")
            
        # Check for calculated columns
        required_cols = ['Mobilization (days)', 'Deployment (days)', 'Production (days)', 
                        'Recovery (days)', 'Demobilization (days)', 'Project Duration']
        missing_cols = [col for col in required_cols if col not in enhanced_df.columns]
        if missing_cols:
            errors.append(f"Enhanced file missing columns: {missing_cols}")
            print(f"   ❌ Missing calculated columns!")
        else:
            print(f"   ✓ All calculated columns present")
    except FileNotFoundError:
        errors.append("Enhanced_Streamer_Projects.csv not found")
        print("   ❌ Enhanced file not found!")
    
    # Check 3: Vessel Quarterly Pivot exists
    print("3. Checking Vessel_Quarterly_Pivot_2025.csv...")
    try:
        pivot_df = pd.read_csv("Vessel_Quarterly_Pivot_2025.csv")
        print(f"   ✓ Pivot file loaded: {len(pivot_df)} vessels")
        
        # Check for required columns
        required_q_cols = ['Q1 Days', 'Q2 Days', 'Q3 Days', 'Q4 Days']
        missing_q_cols = [col for col in required_q_cols if col not in pivot_df.columns]
        if missing_q_cols:
            errors.append(f"Pivot file missing columns: {missing_q_cols}")
            print(f"   ❌ Missing quarter columns!")
        else:
            print(f"   ✓ All quarter columns present")
    except FileNotFoundError:
        errors.append("Vessel_Quarterly_Pivot_2025.csv not found")
        print("   ❌ Pivot file not found!")
    
    # Check 4: Quarterly breakdown exists
    print("4. Checking quarterly_breakdown_data.csv...")
    try:
        quarterly_df = pd.read_csv("quarterly_breakdown_data.csv")
        print(f"   ✓ Quarterly breakdown loaded: {len(quarterly_df)} entries")
        
        # Check for required columns
        required_qb_cols = ['Project', 'Vessel', 'Survey Type', 'Quarter', 'Duration']
        missing_qb_cols = [col for col in required_qb_cols if col not in quarterly_df.columns]
        if missing_qb_cols:
            errors.append(f"Quarterly breakdown missing columns: {missing_qb_cols}")
            print(f"   ❌ Missing required columns!")
        else:
            print(f"   ✓ All required columns present")
    except FileNotFoundError:
        errors.append("quarterly_breakdown_data.csv not found")
        print("   ❌ Quarterly breakdown file not found!")
    
    # Check 5: Dated files exist (today's date)
    print("5. Checking dated files...")
    today = datetime.now().strftime('%Y%m%d')
    dated_files = [
        f"Enhanced_Streamer_Projects_{today}.csv",
        f"Vessel_Quarterly_Pivot_2025_{today}.csv",
        f"quarterly_breakdown_data_{today}.csv"
    ]
    
    dated_found = 0
    for dated_file in dated_files:
        try:
            pd.read_csv(dated_file)
            dated_found += 1
        except FileNotFoundError:
            pass
    
    if dated_found == 0:
        warnings.append(f"No dated files found for {today}. Files may be from a previous run.")
        print(f"   ⚠️  No dated files found for today ({today})")
    else:
        print(f"   ✓ Found {dated_found}/3 dated files for {today}")
    
    print()
    print("=" * 60)
    
    # Summary
    if errors:
        print("❌ VALIDATION FAILED")
        print()
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
        if warnings:
            print()
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        print()
        print("Please run: ./update_data.sh or python generate_csv_files.py")
        return False
    elif warnings:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
        print("Data files are valid but may need updating.")
        return True
    else:
        print("✅ VALIDATION PASSED")
        print()
        print("All data files are properly synchronized!")
        return True

if __name__ == '__main__':
    success = validate_data_flow()
    sys.exit(0 if success else 1)
