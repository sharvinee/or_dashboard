import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#########################
# Page Config
st.set_page_config(
    page_title="OR Utilization Dashboard of Q1 2022",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

#########################
# CSS Styling
st.markdown("""
    <style>
    
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        margin-top: 0rem;
        margin-bottom: 0rem;
    }
    
    .stApp header {
        display: none;
    }
    
    body {
        color: #333333;
        background-color: #FFFFFF;
    }
    
    .stApp {
        background-color: #FFFFFF;
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #16A085;
        padding: 0.3rem 0;
        margin-bottom: 0.7rem;
        border-bottom: 2px solid #EEEEEE;
    }
    
    h3, h5 {
        margin-top: 0.5rem;
        margin-bottom: 0rem;
        text-align: center;
    }

    .stRadio > div {
        margin-top: -30px;  
        padding-top: -10px;
        padding-left: -1rem;
    }
                  
    .stPlotlyChart {
        margin-bottom: 0;
    }
    
    footer {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

#########################
def format_time_delta(td):
    #Format timedelta to minutes
    if pd.isna(td):
        return "N/A"
    total_seconds = td.total_seconds()
    minutes = int(total_seconds / 60)
    return f"{minutes} mins"

def load_data():
    df = pd.read_csv("df_transformed.csv")
    
    # Convert date columns to datetime
    df['date'] = pd.to_datetime(df['date'])
    date_columns = ['or_schedule', 'wheels_in', 'start_time', 'end_time', 'wheels_out']
    
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])
    
    # Handle turnover_time column (convert string to timedelta)
    if 'turnover_time' in df.columns:
        # If turnover_time is already in the data
        df['turnover_time'] = pd.to_timedelta(df['turnover_time'])
    else:
        # Calculate turnover time if it's not already there
        df["turnover_time"] = df.groupby(["date", "or_suite"]).apply(
            lambda group: group["wheels_in"] - group["wheels_out"].shift(1)
        ).reset_index(level=[0, 1], drop=True)
    
    return df

def calculate_duration_minutes(row):
    #Calculate procedure duration in minutes
    if pd.isna(row['duration']):
        return np.nan
    
    duration = pd.to_timedelta(row['duration'])
    return duration.total_seconds() / 60

#########################
# Load Data
df = load_data()

# Calculate duration in minutes
df['duration_minutes'] = df.apply(calculate_duration_minutes, axis=1)

#########################
# Sidebar Filters
with st.sidebar:
    st.write("Filter Options")
    
    # Month filter
    # month_list = ["ALL"] + sorted(list(df.month.unique()))
    # selected_month = st.selectbox("Select Month", month_list)
    month_list = ["ALL", "January", "February", "March"]
    selected_month = st.selectbox("Select Month", month_list)
    
    # OR suite filter
    or_suite_list = ["ALL"] + sorted([str(x) for x in df.or_suite.unique()])
    selected_or_suite = st.selectbox("Select OR Suite", or_suite_list)
    
    # Apply filters
    if selected_month != "ALL":
        filtered_df = df[df.month == selected_month]
    else:
        filtered_df = df.copy()
        
    if selected_or_suite != "ALL":
        filtered_df = filtered_df[filtered_df.or_suite == int(selected_or_suite)]
    
    # Define service filtered df
    service_filtered_df = filtered_df.copy()
    
    # Use a consistent color theme
    selected_color_theme = 'blues'

#########################
# Main Dashboard
# Title
st.markdown('<div class="dashboard-title">OR Utilization Dashboard of Q1 2022</div>', unsafe_allow_html=True)

# KPI Metrics - Top Row
col1, col2 = st.columns(2)

# KPI 1:Average Turnover Time
with col1:
    avg_turnover = filtered_df['turnover_time'].mean()
    if pd.isna(avg_turnover):
        avg_turnover_mins = "N/A"
        kpi_color = "#555555"  # Neutral gray for N/A
    else:
        avg_turnover_mins = f"{int(avg_turnover.total_seconds() / 60)} mins"
        
        # Determine color based on turnover time
        if avg_turnover.total_seconds() / 60 > 30:
            kpi_color = "#FF4136"  # Red for over 30 minutes
        else:
            kpi_color = "#2ECC40"  # Green for under 30 minutes
    
    kpi_box = f"""
    <div style="background-color: #F7F7F7; border: 1px solid #DDDDDD; border-radius: 10px; padding: 10px 10px 5px 10px; margin-bottom: 0.3rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #555555; margin-bottom: 0.2rem;">Average Turnover Time</div>
        <div style="font-size: 2rem; color: {kpi_color}; font-weight: 700;">{avg_turnover_mins}</div>
    </div>
    """
    st.markdown(kpi_box, unsafe_allow_html=True)


# KPI 2: Average Case Duration
with col2:
    avg_duration = filtered_df['duration_minutes'].mean()
    if pd.isna(avg_duration):
        avg_duration_mins = "N/A"
    else:
        avg_duration_mins = f"{int(avg_duration)} mins"
    
    kpi_box = f"""
    <div style="background-color: #F7F7F7; border: 1px solid #DDDDDD; border-radius: 10px; padding: 10px 10px 5px 10px; margin-bottom: 0.3rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); text-align: center;">
        <div style="font-size: 0.9rem; color: #555555; margin-bottom: 0.2rem;">Average Case Duration</div>
        <div style="font-size: 2rem; color: #0068C9; font-weight: 700;">{avg_duration_mins}</div>
    </div>
    """
    st.markdown(kpi_box, unsafe_allow_html=True)

# Second Row: OR Status Table and Case Volume Chart
col3, spacer, col4 = st.columns([0.7, 0.1, 2])

# OR Status Table
with col3:
    
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    
    st.markdown("<h5>OR Suite Status at the Start of Last Day</h5>", unsafe_allow_html=True)
    
    # Find the last day in the dataset
    last_day = df['date'].max()
    start_of_day = df[df['date'] == last_day]['or_schedule'].min()
    
    # Get unique OR suites
    unique_or = df[df['date'] == last_day]['or_suite'].unique()
    
    # Determine OR status at beginning of last day
    or_status = {}
    
    for suite in unique_or:
        suite_data = df[df['or_suite'] == suite]
        if not suite_data.empty and (suite_data['start_time'] >= start_of_day).any():
            or_status[suite] = "In Use/Scheduled"
        else:
            or_status[suite] = "Available"
    
    # Create status dataframe
    or_status_df = pd.DataFrame(list(or_status.items()), columns=['OR Suite', 'Status'])
    # Sort by OR Suite number
    or_status_df = or_status_df.sort_values('OR Suite')
    
    # Display as a Streamlit dataframe with custom styling
    st.dataframe(
        or_status_df,
        column_config={
            "OR Suite": st.column_config.NumberColumn("OR Suite", width="small"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
        },
        hide_index=True,
        use_container_width=True,
        height=315
    )

# Case Volume Chart with Popover Filter
with col4:
    st.write("")
    st.markdown("<h3>Case Volume by Operation Room</h3>", unsafe_allow_html=True)
    
    with st.container():
        # Create a row for the chart header and filter
        header_col1, header_col2 = st.columns([5, 1])
        
        with header_col1:
            st.write("")  # Empty space
        
        with header_col2:
            with st.popover("Filter by"):
                # Filter options as radio buttons
                if 'chart_filter' not in st.session_state:
                    st.session_state.chart_filter = "None"
                
                st.session_state.chart_filter = st.radio(
                    "", 
                    ["None", "Service", "CPT Description"], 
                    index=["None", "Service", "CPT Description"].index(st.session_state.chart_filter),
                    horizontal=True
                )
        
        # Get the filter from session state
        if 'chart_filter' not in st.session_state:
            st.session_state.chart_filter = "None"
            
        active_filter = st.session_state.chart_filter
        
        # Group data based on filter
        if active_filter == "None":
            # Group by OR suite only
            case_volume = filtered_df.groupby(['or_suite']).size().reset_index(name='case_count')
            color_column = None
        elif active_filter == "Service":
            # Group by OR suite and service
            case_volume = filtered_df.groupby(['or_suite', 'service']).size().reset_index(name='case_count')
            color_column = 'service'
        elif active_filter == "CPT Description":
            # Group by OR suite and CPT description
            case_volume = filtered_df.groupby(['or_suite', 'cpt_description']).size().reset_index(name='case_count')
            color_column = 'cpt_description'
        
        # Create bar chart
        if not case_volume.empty:
            if active_filter == "None":
                # Simple bar chart without color grouping
                fig = px.bar(
                    case_volume,
                    x='or_suite',
                    y='case_count',
                    labels={'case_count': 'Number of Cases', 'or_suite': 'OR Suite'},
                    color_discrete_sequence=['#D35400']  # Use a single color
                )
            else:
                # Stacked bar chart with color grouping
                fig = px.bar(
                    case_volume,
                    x='or_suite',
                    y='case_count',
                    color=color_column,
                    barmode='stack',
                    labels={'case_count': 'Number of Cases', 'or_suite': 'OR Suite'},
                )
            
            fig.update_layout(
                xaxis_title='OR Suite',
                yaxis_title='Number of Cases',
                legend_title=active_filter,
                height=400,
                margin=dict(t=1, b=2, l=5, r=5),
                xaxis=dict(
                    type='category',
                    categoryorder='array',
                    categoryarray=sorted([str(x) for x in filtered_df.or_suite.unique()])
                ),
                # Set light theme for chart
                paper_bgcolor='rgba(255,255,255,0)',
                plot_bgcolor='rgba(247,247,247,0.5)',
                barcornerradius=3
            )
            
            # Update grid and axis colors for better visibility
            fig.update_xaxes(gridcolor='#DDDDDD', showgrid=True, zeroline=False, showline=True, linecolor='#CCCCCC')
            fig.update_yaxes(gridcolor='#DDDDDD', showgrid=True, zeroline=False, showline=True, linecolor='#CCCCCC')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available with current filters.")

# Compact footer
st.markdown('<div style="text-align: center; font-size: 0.8rem; margin-top: 0; padding-top: 0;">OR Utilization Dashboard | Q1 2022 | Data from 2022-01-03 to 2022-03-31</div>', unsafe_allow_html=True)