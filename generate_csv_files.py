#!/usr/bin/env python3
"""
Script to generate the CSV files required by the Streamlit dashboard.
Based on the Jupyter notebook: Shearwater Competitor Information.ipynb

Prerequisites:
- Requires 'Streamer Projects - SWG - AI.csv' in the current directory
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
import shutil

def merge_date_ranges(date_ranges):
    """
    Merge overlapping date ranges and return the total unique days.
    Prevents double-counting when a vessel works on multiple overlapping projects.
    """
    if not date_ranges:
        return 0
    
    # Sort by start date
    sorted_ranges = sorted(date_ranges, key=lambda x: x[0])
    
    # Merge overlapping ranges
    merged = [sorted_ranges[0]]
    for current_start, current_end in sorted_ranges[1:]:
        last_start, last_end = merged[-1]
        
        # If current range overlaps or is adjacent to the last range, merge them
        if current_start <= last_end + pd.Timedelta(days=1):
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            # No overlap, add as new range
            merged.append((current_start, current_end))
    
    # Calculate total days across all merged ranges
    total_days = sum((end - start).days + 1 for start, end in merged)
    return total_days

def calculate_days_in_quarter(start_dt, end_dt, year, quarter):
    """Calculate how many days a project overlaps with a specific quarter."""
    qtr_start_month = (quarter - 1) * 3 + 1
    qtr_start = pd.Timestamp(year=year, month=qtr_start_month, day=1)
    
    if quarter == 4:
        qtr_end = pd.Timestamp(year=year, month=12, day=31)
    else:
        next_qtr_start = pd.Timestamp(year=year, month=qtr_start_month + 3, day=1)
        qtr_end = next_qtr_start - pd.Timedelta(days=1)
    
    # Calculate overlap
    overlap_start = max(start_dt, qtr_start)
    overlap_end = min(end_dt, qtr_end)
    
    if overlap_start > overlap_end:
        return 0
    
    return (overlap_end - overlap_start).days + 1

def remove_old_dated_files(base_name, date_str):
    """Remove old dated files for the same base name, keeping only today's file."""
    pattern = f"{base_name}_"
    for filename in os.listdir('.'):
        if filename.startswith(pattern) and filename.endswith('.csv') and filename != f"{base_name}_{date_str}.csv":
            try:
                os.remove(filename)
                print(f"  Removed old file: {filename}")
            except Exception as e:
                print(f"  Warning: Could not remove {filename}: {e}")

def main():
    # Check if source file exists
    source_file = "Streamer Projects - SWG - AI.csv"
    if not os.path.exists(source_file):
        print(f"ERROR: Source file '{source_file}' not found!")
        print(f"Please ensure the file exists in the current directory: {os.getcwd()}")
        sys.exit(1)
    
    print(f"Loading data from {source_file}...")
    
    # Load the raw data
    df = pd.read_csv(source_file)
    print(f"Loaded {len(df)} projects")
    
    # Convert date columns to datetime
    date_cols = ["Mobilisation Start", "Deployment Start", "Production Start", 
                 "Production End", "Retrieval End", "Demobilisation End"]
    
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate phase durations
    print("\nCalculating phase durations...")
    df['Mobilization (days)'] = (df['Deployment Start'] - df['Mobilisation Start']).dt.days
    df['Deployment (days)'] = (df['Production Start'] - df['Deployment Start']).dt.days
    df['Production (days)'] = (df['Production End'] - df['Production Start']).dt.days
    df['Recovery (days)'] = (df['Retrieval End'] - df['Production End']).dt.days
    df['Demobilization (days)'] = (df['Demobilisation End'] - df['Retrieval End']).dt.days
    df['Project Duration'] = (df['Demobilisation End'] - df['Mobilisation Start']).dt.days
    
    # Get current date string for file naming
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Remove old dated files before creating new ones
    remove_old_dated_files("Enhanced_Streamer_Projects", date_str)
    
    # Save Enhanced_Streamer_Projects.csv with date
    enhanced_filename = f"Enhanced_Streamer_Projects_{date_str}.csv"
    print(f"\nSaving {enhanced_filename}...")
    df.to_csv(enhanced_filename, index=False)
    # Also save without date for backward compatibility
    df.to_csv("Enhanced_Streamer_Projects.csv", index=False)
    print(f"✓ Created {enhanced_filename} with {len(df)} rows and {len(df.columns)} columns")
    print(f"✓ Created Enhanced_Streamer_Projects.csv (for backward compatibility)")
    
    # Generate Vessel Quarterly Pivot 2025
    print("\nGenerating Vessel Quarterly Pivot 2025...")
    
    # Filter to projects that overlap with 2025
    df_2025 = df[
        (df['Mobilisation Start'].dt.year <= 2025) & 
        (df['Demobilisation End'].dt.year >= 2025)
    ].copy()
    
    print(f"Found {len(df_2025)} projects in 2025")
    
    # Prepare data for quarterly aggregation
    quarterly_data = []
    
    for _, row in df_2025.iterrows():
        if pd.isna(row['Mobilisation Start']) or pd.isna(row['Demobilisation End']):
            continue
        
        vessel = row['Vessel']
        start = row['Mobilisation Start']
        end = row['Demobilisation End']
        
        # Parse day rate (handle $, commas, spaces, #DIV/0! errors)
        # Note: Source data uses 'Day Rate' column which may be empty or contain errors
        day_rate_str = str(row.get('Day Rate', '')).replace('$', '').replace(',', '').replace(' ', '').replace('#DIV/0!', '').strip()
        day_rate = float(day_rate_str) if day_rate_str and day_rate_str != 'nan' else 0
        
        # Note: Source data does not have a 'Total Revenue' column
        # Revenue would need to be calculated separately or added to source data
        revenue = 0
        
        # Calculate days in each quarter of 2025
        for quarter in [1, 2, 3, 4]:
            days = calculate_days_in_quarter(start, end, 2025, quarter)
            if days > 0:
                quarterly_data.append({
                    'Vessel': vessel,
                    'Quarter': f'Q{quarter} 2025',
                    'Days': days,
                    'Day Rate': day_rate,
                    'Revenue': revenue,
                    'Start': start,
                    'End': end
                })
    
    quarterly_df = pd.DataFrame(quarterly_data)
    
    # Group by vessel and quarter to aggregate
    vessel_quarters = []
    
    for vessel in sorted(quarterly_df['Vessel'].unique()):
        vessel_data = {'Vessel': vessel}
        
        for quarter in [1, 2, 3, 4]:
            q_name = f'Q{quarter} 2025'
            q_data = quarterly_df[(quarterly_df['Vessel'] == vessel) & (quarterly_df['Quarter'] == q_name)]
            
            if len(q_data) > 0:
                # Get date ranges for this vessel in this quarter
                # IMPORTANT: Use quarter-specific overlap ranges, not full project ranges
                qtr_start_month = (quarter - 1) * 3 + 1
                qtr_start = pd.Timestamp(year=2025, month=qtr_start_month, day=1)
                if quarter == 4:
                    qtr_end = pd.Timestamp(year=2025, month=12, day=31)
                else:
                    next_qtr_start = pd.Timestamp(year=2025, month=qtr_start_month + 3, day=1)
                    qtr_end = next_qtr_start - pd.Timedelta(days=1)
                
                # Calculate quarter-specific date ranges for overlap merging
                date_ranges = []
                for _, row in q_data.iterrows():
                    overlap_start = max(row['Start'], qtr_start)
                    overlap_end = min(row['End'], qtr_end)
                    if overlap_start <= overlap_end:
                        date_ranges.append((overlap_start, overlap_end))
                
                unique_days = merge_date_ranges(date_ranges)
                
                # Calculate weighted average day rate
                total_day_rate_weighted = (q_data['Day Rate'] * q_data['Days']).sum()
                total_days = q_data['Days'].sum()
                avg_day_rate = total_day_rate_weighted / total_days if total_days > 0 else 0
                
                # Calculate total cost and revenue
                total_cost = avg_day_rate * unique_days
                total_revenue = q_data['Revenue'].sum()
                
                vessel_data[f'Q{quarter} Days'] = unique_days
                vessel_data[f'Q{quarter} Avg Day Rate'] = avg_day_rate
                vessel_data[f'Q{quarter} Total Cost'] = total_cost
                vessel_data[f'Q{quarter} Revenue'] = total_revenue
            else:
                vessel_data[f'Q{quarter} Days'] = 0
                vessel_data[f'Q{quarter} Avg Day Rate'] = 0
                vessel_data[f'Q{quarter} Total Cost'] = 0
                vessel_data[f'Q{quarter} Revenue'] = 0
        
        vessel_quarters.append(vessel_data)
    
    vessel_pivot_df = pd.DataFrame(vessel_quarters)
    
    # Remove old dated files before creating new ones
    remove_old_dated_files("Vessel_Quarterly_Pivot_2025", date_str)
    
    # Save Vessel_Quarterly_Pivot_2025.csv with date
    pivot_filename = f"Vessel_Quarterly_Pivot_2025_{date_str}.csv"
    print(f"\nSaving {pivot_filename}...")
    vessel_pivot_df.to_csv(pivot_filename, index=False)
    # Also save without date for backward compatibility
    vessel_pivot_df.to_csv("Vessel_Quarterly_Pivot_2025.csv", index=False)
    print(f"✓ Created {pivot_filename} with {len(vessel_pivot_df)} rows and {len(vessel_pivot_df.columns)} columns")
    print(f"✓ Created Vessel_Quarterly_Pivot_2025.csv (for backward compatibility)")
    
    # Generate quarterly breakdown data with duration column
    print("\nGenerating Quarterly Breakdown Data...")
    
    # Build quarterly breakdown for each project, collecting date ranges per vessel-quarter
    vessel_quarter_projects = {}  # Key: (vessel, quarter), Value: list of (project_name, survey_type, date_ranges)
    
    for idx, project_row in df_2025.iterrows():
        if pd.isna(project_row['Mobilisation Start']) or pd.isna(project_row['Demobilisation End']):
            continue
        
        project_name = project_row['Survey Name']
        vessel = project_row.get('Vessel', None)
        survey_type = project_row.get('Activity', None)
        mobil_start = project_row['Mobilisation Start']
        demobil_end = project_row['Demobilisation End']
        
        # Calculate days in each quarter of 2025
        for quarter in [1, 2, 3, 4]:
            days_in_qtr = calculate_days_in_quarter(mobil_start, demobil_end, 2025, quarter)
            if days_in_qtr > 0:
                # Calculate the actual date range for this project in this quarter
                qtr_start_month = (quarter - 1) * 3 + 1
                qtr_start = pd.Timestamp(year=2025, month=qtr_start_month, day=1)
                if quarter == 4:
                    qtr_end = pd.Timestamp(year=2025, month=12, day=31)
                else:
                    next_qtr_start = pd.Timestamp(year=2025, month=qtr_start_month + 3, day=1)
                    qtr_end = next_qtr_start - pd.Timedelta(days=1)
                
                overlap_start = max(mobil_start, qtr_start)
                overlap_end = min(demobil_end, qtr_end)
                
                key = (vessel, quarter)
                if key not in vessel_quarter_projects:
                    vessel_quarter_projects[key] = []
                vessel_quarter_projects[key].append({
                    'project': project_name,
                    'survey_type': survey_type,
                    'date_range': (overlap_start, overlap_end)
                })
    
    # Create separate records for each project (not merged)
    quarterly_records = []
    
    for (vessel, quarter), projects in vessel_quarter_projects.items():
        # Create a separate record for each project
        for project_info in projects:
            project_name = project_info['project']
            survey_type = project_info['survey_type']
            date_range = project_info['date_range']
            
            # Calculate duration for this specific project in this quarter
            duration = (date_range[1] - date_range[0]).days + 1
            
            quarterly_records.append({
                'Project': project_name,
                'Vessel': vessel,
                'Survey Type': str(survey_type) if pd.notna(survey_type) else '',
                'Quarter': f'Q{quarter}-2025',
                'Duration': duration  # Duration in days for this specific project
            })
    
    quarterly_breakdown_df = pd.DataFrame(quarterly_records)
    
    # Sort by vessel and quarter for better readability
    quarterly_breakdown_df = quarterly_breakdown_df.sort_values(['Vessel', 'Quarter'])
    
    # Remove old dated files before creating new ones
    remove_old_dated_files("quarterly_breakdown_data", date_str)
    
    # Save quarterly_breakdown_data.csv with date
    quarterly_filename = f"quarterly_breakdown_data_{date_str}.csv"
    print(f"\nSaving {quarterly_filename}...")
    quarterly_breakdown_df.to_csv(quarterly_filename, index=False)
    # Also save without date for backward compatibility
    quarterly_breakdown_df.to_csv("quarterly_breakdown_data.csv", index=False)
    print(f"✓ Created {quarterly_filename} with {len(quarterly_breakdown_df)} rows and {len(quarterly_breakdown_df.columns)} columns")
    print(f"✓ Created quarterly_breakdown_data.csv (for backward compatibility)")
    
    print("\n✅ All CSV files generated successfully!")
    print("\nGenerated files with dates (overwrites if run same day):")
    print(f"  - {enhanced_filename}")
    print(f"  - {pivot_filename}")
    print(f"  - {quarterly_filename}")
    print("\nBackward compatibility files (without dates):")
    print("  - Enhanced_Streamer_Projects.csv")
    print("  - Vessel_Quarterly_Pivot_2025.csv")
    print("  - quarterly_breakdown_data.csv")

if __name__ == '__main__':
    main()
