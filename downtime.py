import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
from warnings import filterwarnings
import streamlit as st
filterwarnings("ignore")

st.title("Downtime Analysis")

df = pd.read_excel(r"C:\Users\bung\Downloads\Surge\Downtime\ALL.xlsx", engine="openpyxl")
st.write("Raw Data", df)

df['formatted_datetime'] = pd.to_datetime(df['Time'], errors='coerce')
df = df.dropna(subset=['formatted_datetime'])

pivoted = df.pivot_table(
    index='formatted_datetime',
    columns='Name',
    values='Status',
    aggfunc='first'
)
pivoted.columns = [
    'Flare_Pilot_Status', 
    'Combustor_Pilot_Status', 
    'Process_SD_PR1_Status', 
    'PLC_ESD_Tripped_Shutdown'
]
pivoted = pivoted.reset_index()
st.write("Pivoted Data", pivoted.head())

pivoted['time_diff'] = pivoted['formatted_datetime'].diff().dt.total_seconds().fillna(0)
total_time = pivoted['time_diff'].sum()

# Exclude overlap with Process_SD_PR1_Status for Flare/Combustor
flare_time_down = pivoted.loc[
    (pivoted['Flare_Pilot_Status'] == 1) & (pivoted['Process_SD_PR1_Status'] != 1),
    'time_diff'
].sum()
combustor_time_down = pivoted.loc[
    (pivoted['Combustor_Pilot_Status'] == 1) & (pivoted['Process_SD_PR1_Status'] != 1),
    'time_diff'
].sum()
process_sd_time_down = pivoted.loc[
    pivoted['Process_SD_PR1_Status'] == 1,
    'time_diff'
].sum()
plc_esd_time_down = pivoted.loc[
    pivoted['PLC_ESD_Tripped_Shutdown'] == 0,
    'time_diff'
].sum()

flare_percent_time = ((flare_time_down / total_time) * 100)
combustor_percent_time = ((combustor_time_down / total_time) * 100)
process_sd_percent_time = ((process_sd_time_down / total_time) * 100)
plc_esd_percent_time = ((plc_esd_time_down / total_time) * 100)

st.subheader("Downtime Percentages by Time")
st.write(f"Flare downtime: {flare_percent_time:.2f}%")
st.write(f"Combustor downtime: {combustor_percent_time:.2f}%")
st.write(f"Process SD downtime: {process_sd_percent_time:.2f}%")
st.write(f"PLC ESD downtime: {plc_esd_percent_time:.2f}%")

plt.figure(figsize=(10, 6))
downtime_percentages = {
    'Flare Pilot': flare_percent_time,
    'Combustor Pilot': combustor_percent_time,
    'Process SD PR1': process_sd_percent_time,
    'PLC ESD Tripped Shutdown': plc_esd_percent_time
}
sns.barplot(x=list(downtime_percentages.keys()), y=list(downtime_percentages.values()))
plt.title('Downtime Percentages by Component')
plt.xlabel('Component')
plt.ylabel('Downtime Percentage (%)')
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()

# Counts not based on time, just how many times each component was down (excluding overlap)
downtime_counts = {
    'Flare_Pilot_Status': ((pivoted['Flare_Pilot_Status'] == 1) & (pivoted['Process_SD_PR1_Status'] != 1)).sum(),
    'Combustor_Pilot_Status': ((pivoted['Combustor_Pilot_Status'] == 1) & (pivoted['Process_SD_PR1_Status'] != 1)).sum(),
    'Process_SD_PR1_Status': (pivoted['Process_SD_PR1_Status'] == 1).sum(),
    'PLC_ESD_Tripped_Shutdown': (pivoted['PLC_ESD_Tripped_Shutdown'] == 0).sum()
}
total_counts = {
    'Flare_Pilot_Status': pivoted['Flare_Pilot_Status'].count(),
    'Combustor_Pilot_Status': pivoted['Combustor_Pilot_Status'].count(),
    'Process_SD_PR1_Status': pivoted['Process_SD_PR1_Status'].count(),
    'PLC_ESD_Tripped_Shutdown': pivoted['PLC_ESD_Tripped_Shutdown'].count()
}

st.subheader("Downtime Counts as Percentage of Total Occurrences")
for i in downtime_counts:
    st.write(f"{i} down: {downtime_counts[i]} times, total: {total_counts[i]} times, percentage: {downtime_counts[i] / total_counts[i] * 100:.2f}%")

plt.figure(figsize=(10, 6))
sns.barplot(x=list(downtime_counts.keys()), y=[(downtime_counts[i] / total_counts[i]) * 100 for i in downtime_counts])
plt.title('Downtime Counts as Percentage of Total Occurrences')
plt.xlabel('Component')
plt.ylabel('Downtime Percentage (%)')
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()