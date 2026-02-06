#!/usr/bin/env python3
"""
Script to generate the CSV files required by the Streamlit dashboard.
Based on the Jupyter notebook: Shearwater Competitor Information.ipynb
"""

import pandas as pd
import numpy as np
from datetime import datetime

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

def main():
    print("Loading data from Streamer Projects - SWG - AI.csv...")
    
    # Load the raw data
    df = pd.read_csv("Streamer Projects - SWG - AI.csv")
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
    
    # Save Enhanced_Streamer_Projects.csv
    print("\nSaving Enhanced_Streamer_Projects.csv...")
    df.to_csv("Enhanced_Streamer_Projects.csv", index=False)
    print(f"✓ Created Enhanced_Streamer_Projects.csv with {len(df)} rows and {len(df.columns)} columns")
    
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
        
        # Parse day rate and revenue (handle $, commas, spaces)
        day_rate_str = str(row.get('Avg. Day Rate', '')).replace('$', '').replace(',', '').replace(' ', '').strip()
        day_rate = float(day_rate_str) if day_rate_str and day_rate_str != 'nan' else 0
        
        revenue_str = str(row.get('Total Revenue', '')).replace('$', '').replace(',', '').replace(' ', '').strip()
        revenue = float(revenue_str) if revenue_str and revenue_str != 'nan' else 0
        
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
                date_ranges = [(row['Start'], row['End']) for _, row in q_data.iterrows()]
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
    
    # Save Vessel_Quarterly_Pivot_2025.csv
    print("\nSaving Vessel_Quarterly_Pivot_2025.csv...")
    vessel_pivot_df.to_csv("Vessel_Quarterly_Pivot_2025.csv", index=False)
    print(f"✓ Created Vessel_Quarterly_Pivot_2025.csv with {len(vessel_pivot_df)} rows and {len(vessel_pivot_df.columns)} columns")
    
    print("\n✅ All CSV files generated successfully!")
    print("\nGenerated files:")
    print("  - Enhanced_Streamer_Projects.csv")
    print("  - Vessel_Quarterly_Pivot_2025.csv")

if __name__ == '__main__':
    main()
