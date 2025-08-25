import streamlit as st
import pandas as pd
import os
import time 
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Set page configuration
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="📊",
    layout="wide"
) 

# Auto-refresh every 5 seconds
count = st_autorefresh(interval=5000, key="attendance_refresh")

# Get current date and timestamp
ts = time.time()
current_date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
current_timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

# App title and description
st.title("📊 Face Recognition Attendance System")
st.markdown(f"**Current Date:** {current_date} | **Current Time:** {current_timestamp}")

# Check if Attendance directory exists
if not os.path.exists('Attendance'):
    st.warning("⚠️ Attendance directory not found. No attendance records available.")
    st.stop()

# Get all attendance files
attendance_files = [f for f in os.listdir('Attendance') if f.startswith('Attendance_') and f.endswith('.csv')]

if not attendance_files:
    st.warning("⚠️ No attendance records found.")
    st.stop()

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Today's Attendance", "All Records", "Statistics"])

with tab1:
    st.header("📅 Today's Attendance")
    
    # Try to load today's attendance file
    today_file = f"Attendance/Attendance_{current_date}.csv"
    
    if os.path.exists(today_file):
        try:
            df_today = pd.read_csv(today_file)
            st.dataframe(df_today, use_container_width=True)
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df_today))
            with col2:
                st.metric("Unique Persons", df_today['NAME'].nunique())
            with col3:
                latest_time = df_today['TIME'].max() if not df_today.empty else "N/A"
                st.metric("Latest Entry", latest_time)
                
        except Exception as e:
            st.error(f"Error reading today's attendance file: {e}")
    else:
        st.info("No attendance recorded for today yet.")

with tab2:
    st.header("📋 All Attendance Records")
    
    # Let user select which file to view
    selected_file = st.selectbox("Select date to view:", attendance_files)
    
    if selected_file:
        try:
            df_all = pd.read_csv(f"Attendance/{selected_file}")
            st.dataframe(df_all, use_container_width=True)
            
            # Show file statistics
            st.subheader("File Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Total entries:** {len(df_all)}")
                st.write(f"**Date:** {selected_file.replace('Attendance_', '').replace('.csv', '')}")
            with col2:
                st.write(f"**Unique persons:** {df_all['NAME'].nunique()}")
                st.write(f"**Time range:** {df_all['TIME'].min()} to {df_all['TIME'].max()}")
                
        except Exception as e:
            st.error(f"Error reading file {selected_file}: {e}")

with tab3:
    st.header("📈 Attendance Statistics")
    
    # Load all data for statistics
    all_data = []
    for file in attendance_files:
        try:
            df = pd.read_csv(f"Attendance/{file}")
            df['DATE'] = file.replace('Attendance_', '').replace('.csv', '')
            all_data.append(df)
        except:
            continue
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Overall statistics
        st.subheader("Overall Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(combined_df))
        with col2:
            st.metric("Unique Persons", combined_df['NAME'].nunique())
        with col3:
            st.metric("Days Recorded", len(attendance_files))
        
        # Person-wise attendance
        st.subheader("Attendance by Person")
        person_counts = combined_df['NAME'].value_counts()
        st.bar_chart(person_counts)
        
        # Daily attendance trend
        st.subheader("Daily Attendance Trend")
        daily_counts = combined_df['DATE'].value_counts().sort_index()
        st.line_chart(daily_counts)
    else:
        st.info("No data available for statistics.")

# Footer
st.markdown("---")
st.caption("Face Recognition Attendance System - Auto-refreshing every 5 seconds")
