import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Set page configuration
st.set_page_config(page_title="SWG Competitor Analysis Dashboard", layout="wide")

# Title
st.title("Shearwater Competitor Analysis Dashboard")

# Load the data
@st.cache_data
def load_data():
    """Load all required data files"""
    streamer_df = pd.read_csv("Enhanced_Streamer_Projects.csv")
    vessel_pivot_df = pd.read_csv("Vessel_Quarterly_Pivot_2025.csv")
    
    # Strip whitespace from column names
    streamer_df.columns = streamer_df.columns.str.strip()
    vessel_pivot_df.columns = vessel_pivot_df.columns.str.strip()
    
    # Convert date columns to datetime
    date_cols = ["Mobilisation Start", "Deployment Start", "Production Start", 
                 "Production End", "Retrieval End", "Demobilisation End"]
    for col in date_cols:
        streamer_df[col] = pd.to_datetime(streamer_df[col], errors='coerce')
    
    return streamer_df, vessel_pivot_df

# Load data
streamer_df, vessel_pivot_df = load_data()

# Filter to only 2025 projects
streamer_df_2025 = streamer_df[
    (streamer_df['Mobilisation Start'].dt.year == 2025) | 
    (streamer_df['Demobilisation End'].dt.year == 2025)
].copy()

# Define vessel order (11 vessels total, Island Pride as charter)
vessel_order = [
    'SW Bly',
    'SW Tasman', 
    'SW Gallien',
    'Amazon Warrior',
    'Oceanic Sirius',
    'Amazon Conqueror',
    'Oceanic Vega',
    'SW Duchess',
    'SW Thuridur',
    'Island Pride (Charter)',
    'SW Empress'
]

# Map Island Pride to Island Pride (Charter)
streamer_df_2025['Vessel_Display'] = streamer_df_2025['Vessel'].apply(
    lambda x: 'Island Pride (Charter)' if x == 'Island Pride' else x
)

# Create Gantt chart data
def create_gantt_data(df):
    """Create data for Gantt chart with project duration and non-productive time"""
    tasks = []
    
    # Sort by vessel and start date
    df_sorted = df.sort_values(['Vessel_Display', 'Mobilisation Start'])
    
    # Track first start and last end date for each vessel
    vessel_first_start = {}
    vessel_last_end = {}
    
    for idx, row in df_sorted.iterrows():
        if pd.isna(row['Mobilisation Start']) or pd.isna(row['Demobilisation End']):
            continue
        
        vessel = row['Vessel_Display']
        if vessel not in vessel_order:
            continue
            
        # Create legend label (Country + Type of Survey)
        country = str(row['Country']) if pd.notna(row['Country']) else 'Unknown'
        survey_type_raw = row['Activity']
        survey_type = 'Unknown'
        
        # Handle survey type - check for NaN/None first, then convert to string
        if pd.notna(survey_type_raw):
            survey_type = str(survey_type_raw)
        
        # If survey type is still unknown, try to infer from Survey Name
        if survey_type == 'Unknown':
            # Try to infer from Survey Name column
            survey_name = str(row['Survey Name'])
            if '2D' in survey_name:
                survey_type = '2D'
            elif '3D' in survey_name:
                survey_type = '3D'
            elif '4D' in survey_name:
                survey_type = '4D'
            elif 'OBN' in survey_name:
                survey_type = 'OBN'
            else:
                survey_type = 'Survey'
        legend = f"{country} {survey_type}"
        
        # Get Survey Name for labeling
        survey_name_label = str(row['Survey Name']) if pd.notna(row['Survey Name']) else ''
        
        # Determine project type based on Client column
        client = str(row['Client']) if pd.notna(row['Client']) else ''
        is_multi_client = client == 'Multi-Client'
        
        if is_multi_client:
            phase_label = 'MC Project Duration (All Activities)'
        else:
            phase_label = 'Proprietary Project Duration (All Activities)'
        
        # Track first start date for each vessel
        if vessel not in vessel_first_start:
            vessel_first_start[vessel] = row['Mobilisation Start']
        
        # Check for gap with previous project (non-productive time)
        if vessel in vessel_last_end:
            last_end = vessel_last_end[vessel]
            current_start = row['Mobilisation Start']
            # If there's a gap of more than 1 day, add non-productive time
            if (current_start - last_end).days > 1:
                tasks.append(dict(
                    Task=vessel,
                    Start=last_end,
                    Finish=current_start,
                    Resource='Non-Productive Time',
                    Phase='Non-Productive Time',
                    SurveyName='',
                    IsMultiClient=False
                ))
        
        # Single project duration (All Activities) - from Mobilization Start to Demobilization End
        tasks.append(dict(
            Task=vessel,
            Start=row['Mobilisation Start'],
            Finish=row['Demobilisation End'],
            Resource=legend,
            Phase=phase_label,
            SurveyName=survey_name_label,
            IsMultiClient=is_multi_client
        ))
        
        # Update last end date for this vessel
        vessel_last_end[vessel] = row['Demobilisation End']
    
    # Add pre-project idle period for vessels whose first project doesn't start in January
    start_of_2025 = datetime(2025, 1, 1)
    for vessel in vessel_order:
        if vessel in vessel_first_start:
            first_start = vessel_first_start[vessel]
            # If first project doesn't start on or before January 31
            if first_start > datetime(2025, 1, 31):
                tasks.append(dict(
                    Task=vessel,
                    Start=start_of_2025,
                    Finish=first_start,
                    Resource='Non-Productive Time',
                    Phase='Non-Productive Time',
                    SurveyName='',
                    IsMultiClient=False
                ))
    
    # Add non-productive time from last project end to end of 2025 for each vessel
    end_of_2025 = datetime(2025, 12, 31)
    for vessel in vessel_order:
        if vessel in vessel_last_end:
            last_end = vessel_last_end[vessel]
            if last_end < end_of_2025:
                tasks.append(dict(
                    Task=vessel,
                    Start=last_end,
                    Finish=end_of_2025,
                    Resource='Non-Productive Time',
                    Phase='Non-Productive Time',
                    SurveyName='',
                    IsMultiClient=False
                ))
    
    return pd.DataFrame(tasks)

# Create the Gantt chart
gantt_df = create_gantt_data(streamer_df_2025)

# Filter out any rows with NaT values
gantt_df = gantt_df.dropna(subset=['Start', 'Finish'])

# Define phase colors
phase_colors = {
    'MC Project Duration (All Activities)': '#32CD32',         # Green for Multi-Client
    'Proprietary Project Duration (All Activities)': '#00008B', # Dark blue for Proprietary
    'Non-Productive Time': '#D3D3D3'                            # Light gray
}

# Create the Plotly figure
st.header("2025 Vessel Project Timeline")

fig = go.Figure()

# Group tasks by vessel and add them to the figure
for vessel in vessel_order:
    vessel_tasks = gantt_df[gantt_df['Task'] == vessel].sort_values('Start')
    
    if len(vessel_tasks) == 0:
        continue
    
    # Add each phase as a bar
    for idx, task in vessel_tasks.iterrows():
        # Calculate duration in days
        duration = (task['Finish'] - task['Start']).days
        
        # Determine if we should show text on the bar
        show_text = task.get('SurveyName', '') != '' and task['Phase'] != 'Non-Productive Time'
        text_label = task.get('SurveyName', '') if show_text else ''
        
        fig.add_trace(go.Bar(
            name=task['Resource'],
            x=[task['Finish']],
            y=[vessel],
            orientation='h',
            base=task['Start'],
            text=text_label,
            textposition='inside',
            textfont=dict(color='white', size=10),
            marker=dict(
                color=phase_colors.get(task['Phase'], '#D3D3D3'),
                line=dict(color='white', width=0.5)
            ),
            hovertemplate=(
                f"<b>{task['Resource']}</b><br>" +
                f"Vessel: {vessel}<br>" +
                f"Phase: {task['Phase']}<br>" +
                (f"Survey: {task.get('SurveyName', '')}<br>" if task.get('SurveyName', '') else "") +
                f"Start: {task['Start'].strftime('%Y-%m-%d')}<br>" +
                f"End: {task['Finish'].strftime('%Y-%m-%d')}<br>" +
                f"Days: {duration}<br>" +
                "<extra></extra>"
            ),
            showlegend=False
        ))

# Add quarter markers
quarters = [
    ('Q1 2025', datetime(2025, 1, 1), datetime(2025, 3, 31)),
    ('Q2 2025', datetime(2025, 4, 1), datetime(2025, 6, 30)),
    ('Q3 2025', datetime(2025, 7, 1), datetime(2025, 9, 30)),
    ('Q4 2025', datetime(2025, 10, 1), datetime(2025, 12, 31))
]

# Update layout
fig.update_layout(
    barmode='stack',
    height=600,
    xaxis=dict(
        title='',
        type='date',
        tickformat='%b',  # Show month names
        tickmode='array',
        tickvals=pd.date_range(start='2025-01-01', end='2025-12-31', freq='MS'),
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        side='top',  # Put x-axis on top
        showgrid=True,
        gridcolor='lightgray',
        range=['2024-12-15', '2026-01-15']
    ),
    yaxis=dict(
        title='',
        categoryorder='array',
        categoryarray=vessel_order[::-1],  # Reverse order to show from top to bottom
        showgrid=True,
        gridcolor='lightgray'
    ),
    plot_bgcolor='white',
    showlegend=False,
    margin=dict(l=150, r=50, t=100, b=50),
    hovermode='closest'
)

# Add quarter separators as vertical lines
for q_name, q_start, q_end in quarters:
    fig.add_vline(
        x=q_start.timestamp() * 1000,  # Plotly expects milliseconds for date axes (timestamp() returns seconds)
        line_width=2,
        line_dash="dash",
        line_color="gray",
        opacity=0.5
    )
    
    # Add quarter labels
    fig.add_annotation(
        x=q_start + (q_end - q_start) / 2,
        y=1.05,
        text=q_name,
        showarrow=False,
        xref='x',
        yref='paper',
        font=dict(size=12, color='black', family='Arial Black'),
        bgcolor='lightyellow',
        bordercolor='gray',
        borderwidth=1,
        borderpad=4
    )

# Add phase legend manually at the bottom
st.plotly_chart(fig, use_container_width=True)

# Add color legend
st.markdown("### Phase Colors")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🟩 **MC Project Duration (All Activities)**")
with col2:
    st.markdown("🟦 **Proprietary Project Duration (All Activities)**")
with col3:
    st.markdown("⬜ **Non-Productive Time**")

# Add separator
st.markdown("---")

# Create Quarterly Vessel Utilization Table
st.header("Quarterly Vessel Utilization Table")

# Function to calculate quarterly utilization
def calculate_quarterly_utilization(df):
    """Calculate days in project and idle/transit days per vessel per quarter"""
    
    # Define quarters
    quarters = {
        'Q1': (datetime(2025, 1, 1), datetime(2025, 3, 31)),
        'Q2': (datetime(2025, 4, 1), datetime(2025, 6, 30)),
        'Q3': (datetime(2025, 7, 1), datetime(2025, 9, 30)),
        'Q4': (datetime(2025, 10, 1), datetime(2025, 12, 31))
    }
    
    # Days in each quarter
    quarter_days = {
        'Q1': 90,  # Jan (31) + Feb (28 in 2025) + Mar (31)
        'Q2': 91,  # Apr (30) + May (31) + Jun (30)
        'Q3': 92,  # Jul (31) + Aug (31) + Sep (30)
        'Q4': 92   # Oct (31) + Nov (30) + Dec (31)
    }
    
    # Initialize utilization data
    utilization_data = []
    
    for vessel in vessel_order:
        vessel_data = {'Vessel Name': vessel}
        
        # Get all projects for this vessel
        vessel_projects = df[df['Vessel_Display'] == vessel].copy()
        
        for quarter_name, (q_start, q_end) in quarters.items():
            # Calculate days in project for this quarter
            days_in_project = 0
            
            for idx, row in vessel_projects.iterrows():
                if pd.isna(row['Mobilisation Start']) or pd.isna(row['Demobilisation End']):
                    continue
                
                # Get overlap between project and quarter
                project_start = max(row['Mobilisation Start'], q_start)
                project_end = min(row['Demobilisation End'], q_end)
                
                # If there's overlap, count the days
                if project_start <= project_end:
                    days_in_project += (project_end - project_start).days + 1
            
            # Calculate idle/transit days
            total_days_in_quarter = quarter_days[quarter_name]
            idle_transit_days = total_days_in_quarter - days_in_project
            
            vessel_data[f'{quarter_name} Days in Project'] = days_in_project
            vessel_data[f'{quarter_name} Idle/Transit'] = idle_transit_days
        
        utilization_data.append(vessel_data)
    
    return pd.DataFrame(utilization_data)

# Calculate and display the utilization table
utilization_df = calculate_quarterly_utilization(streamer_df_2025)

# Display the table with better formatting
st.dataframe(
    utilization_df,
    use_container_width=True,
    height=450,
    hide_index=True
)

# Add separator
st.markdown("---")

# Display Vessel Quarterly Pivot table
st.header("Vessel Quarterly Pivot 2025")

# Prepare the pivot table (remove Revenue columns)
display_df = vessel_pivot_df.copy()

# Remove all Revenue columns
revenue_cols = [col for col in display_df.columns if 'Revenue' in col]
display_df = display_df.drop(columns=revenue_cols)

# Format numeric columns
numeric_cols = display_df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if 'Day Rate' in col or 'Cost' in col:
        # Format as currency
        display_df[col] = display_df[col].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) and x != 0 else ""
        )
    elif 'Days' in col:
        # Format as integer
        display_df[col] = display_df[col].apply(
            lambda x: f"{int(x)}" if pd.notna(x) and x != 0 else ""
        )

# Replace Island Pride with Island Pride (Charter)
display_df['Vessel'] = display_df['Vessel'].apply(
    lambda x: 'Island Pride (Charter)' if x == 'Island Pride' else x
)

# Display the table
st.dataframe(display_df, use_container_width=True, height=450)

# Footer with instructions
st.markdown("---")
st.markdown("""
### About This Dashboard

This dashboard visualizes the 2025 vessel project timeline and quarterly metrics:

- **Timeline Chart**: Shows project phases across all vessels throughout 2025
  - Each bar represents a project phase colored by activity type
  - Quarters are marked with vertical dashed lines
  - Hover over bars to see project details
  
- **Vessel Quarterly Pivot**: Summarizes vessel utilization by quarter
  - Days: Total days worked in each quarter
  - Avg Day Rate: Average day rate for the quarter
  - Total Cost: Total cost for the quarter
  
**Legend Format**: Country + Type of Survey (e.g., "India 2D")
""")
