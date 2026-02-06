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
    """Create data for Gantt chart with phases"""
    tasks = []
    
    for idx, row in df.iterrows():
        if pd.isna(row['Mobilisation Start']) or pd.isna(row['Demobilisation End']):
            continue
        
        vessel = row['Vessel_Display']
        if vessel not in vessel_order:
            continue
            
        # Create legend label (Country + Type of Survey)
        country = str(row['Country']) if pd.notna(row['Country']) else 'Unknown'
        survey_type = str(row['Activity']) if pd.notna(row['Activity']) else 'Unknown'
        legend = f"{country} {survey_type}"
        
        # Mobilization phase
        if pd.notna(row['Deployment Start']):
            tasks.append(dict(
                Task=vessel,
                Start=row['Mobilisation Start'],
                Finish=row['Deployment Start'],
                Resource=legend,
                Phase='Mobilization'
            ))
        
        # Deployment phase
        if pd.notna(row['Production Start']):
            tasks.append(dict(
                Task=vessel,
                Start=row['Deployment Start'],
                Finish=row['Production Start'],
                Resource=legend,
                Phase='Deployment'
            ))
        
        # Production phase
        if pd.notna(row['Production End']):
            tasks.append(dict(
                Task=vessel,
                Start=row['Production Start'],
                Finish=row['Production End'],
                Resource=legend,
                Phase='Production'
            ))
        
        # Recovery phase
        if pd.notna(row['Retrieval End']):
            tasks.append(dict(
                Task=vessel,
                Start=row['Production End'],
                Finish=row['Retrieval End'],
                Resource=legend,
                Phase='Recovery'
            ))
        
        # Demobilization phase
        if pd.notna(row['Demobilisation End']):
            tasks.append(dict(
                Task=vessel,
                Start=row['Retrieval End'],
                Finish=row['Demobilisation End'],
                Resource=legend,
                Phase='Demobilization'
            ))
    
    return pd.DataFrame(tasks)

# Create the Gantt chart
gantt_df = create_gantt_data(streamer_df_2025)

# Define phase colors
phase_colors = {
    'Mobilization': '#FFD700',     # Yellow
    'Deployment': '#FFA500',        # Orange
    'Production': '#32CD32',        # Green
    'Recovery': '#FFA500',          # Orange
    'Demobilization': '#FFD700',    # Yellow
    'Transit': '#D3D3D3'            # Light gray
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
        
        fig.add_trace(go.Bar(
            name=task['Resource'],
            x=[duration],
            y=[vessel],
            orientation='h',
            base=task['Start'],
            marker=dict(
                color=phase_colors.get(task['Phase'], '#D3D3D3'),
                line=dict(color='white', width=0.5)
            ),
            hovertemplate=(
                f"<b>{task['Resource']}</b><br>" +
                f"Vessel: {vessel}<br>" +
                f"Phase: {task['Phase']}<br>" +
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
        x=q_start.timestamp() * 1000,  # Convert to milliseconds
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
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown("🟨 **Mobilization**")
with col2:
    st.markdown("🟧 **Deployment**")
with col3:
    st.markdown("🟩 **Production**")
with col4:
    st.markdown("🟧 **Recovery**")
with col5:
    st.markdown("🟨 **Demobilization**")

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
