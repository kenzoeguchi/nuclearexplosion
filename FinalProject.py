"""
Name: Kenzo Eguchi
CS230-6
Data: nuclear_explosions.csv
URL: [http://141.133.107.76:8507/]

Description: This program visualizes data on nuclear explosions, allowing users to filter by country and year range.
It includes various interactive widgets and visualizations to enhance the understanding of nuclear yield data over time and by location.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk

# Function to load and preprocess data
# [DA1] Clean the data
@st.cache_data
def load_data():
    # Read data from a CSV file
    data = pd.read_csv(r"C:\Users\kenzo\Downloads\nuclear_explosions.csv")
    # Rename columns for easier access
    data.rename(columns={
        'WEAPON SOURCE COUNTRY': 'Country',
        'Date.Year': 'Year',
        'Location.Cordinates.Latitude': 'Latitude',
        'Location.Cordinates.Longitude': 'Longitude',
        'Data.Yeild.Upper': 'Yield',
        'WEAPON DEPLOYMENT LOCATION': 'Location'}, inplace=True)

    # Clean and fill missing data
    data['Year'] = data['Year'].fillna(data['Year'].mode()[0]).astype(int)
    data['Yield'] = data['Yield'].fillna(data['Yield'].median())
    data['Normalized Yield'] = data['Yield'] / data['Yield'].max()
    data.drop(columns=['Location'], inplace=True)

    # [DA8] Iterating through rows of a DataFrame with iterrows()
    # Add a custom calculation column
    for index, row in data.iterrows():
        data.at[index, 'Custom Calculation'] = row['Yield'] * 0.5

    # Trim whitespace from the country names
    data['Country'] = data['Country'].apply(lambda x: x.strip())
    return data

# Function to count tests in a given year range
def count_tests_in_range(data, start_year, end_year=None):
    if end_year is None:
        end_year = data['Year'].max()
    return data[(data['Year'] >= start_year) & (data['Year'] <= end_year)].shape[0]

# [PY1] A function with two or more parameters, one of which has a default value
# [PY2] A function that returns more than one value
# Function to get statistics of yields
def get_yield_statistics(filtered_data):
    return filtered_data['Yield'].max(), filtered_data['Yield'].min(), filtered_data['Yield'].mean()

# [PY3] A function that returns a value and is called in at least two different places in your program
# Function to filter data based on given parameters
def filter_data(country, start_year, end_year=2024, yield_threshold=None, data=None):
    if data is None:
        data = load_data()
    filtered_data = data[(data['Country'] == country) & (data['Year'].between(start_year, end_year))]
    if yield_threshold is not None:
        filtered_data = filtered_data[filtered_data['Yield'] > yield_threshold]
    return filtered_data

# Load the data using the defined function
data = load_data()

# [ST1] Streamlit widgets: selectbox, slider, number_input
# Setup the sidebar for user inputs
st.sidebar.title("Nuclear Explosions Analysis")
country = st.sidebar.selectbox("Select Country", options=data['Country'].unique())
start_year, end_year = st.sidebar.slider("Select Year Range", min_value=data['Year'].min(), max_value=data['Year'].max(), value=(1970, 1980))
yield_threshold = st.sidebar.slider("Minimum Yield Threshold (Megatons)", 0, 1000, 50)
top_n = st.sidebar.number_input("Select Top N Explosions", min_value=1, value=5, step=1)

# [ST4] Page design features: tabs for organizing presentation
# Setup tabs for organizing the presentation of data
tab1, tab2, tab3, tab4 = st.tabs(["General Overview", "Country Analysis", "Maps and Graphs", "Top Explosions"])

with tab1:
    st.title("General Overview of Nuclear Explosions")
    total_tests = count_tests_in_range(data, start_year, end_year)
    st.write(f"Total nuclear tests from {start_year} to {end_year}: {total_tests}")
    country_summary = {c: get_yield_statistics(filter_data(c, start_year, end_year, None, data)) for c in data['Country'].unique()}
    summary_df = pd.DataFrame.from_dict(country_summary, orient='index', columns=['Max Yield (Megatons)', 'Min Yield (Megatons)', 'Avg Yield (Megatons)'])
    summary_df.index.name = 'Country'
    st.table(summary_df)

with tab2:
    st.title(f"Detailed Analysis for {country}")
    filtered_data = filter_data(country, start_year, end_year, yield_threshold, data)
    total_country_tests = count_tests_in_range(filtered_data, start_year, end_year)
    st.write(f"Total tests for {country} from {start_year} to {end_year}: {total_country_tests}")
    max_yield, min_yield, avg_yield = get_yield_statistics(filtered_data)
    st.write(f"Maximum Yield: {max_yield} Megatons")
    st.write(f"Minimum Yield: {min_yield} Megatons")
    st.write(f"Average Yield: {avg_yield:.2f} Megatons")

  # [VIZ1] Lineplot visualization
  # [VIZ2] Scatterplot visualization
  #[VIZ3] Histogram Visualization
  #[VIZ4] Detailed Map
with tab3:
    st.title("Visualizations")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=filtered_data, x='Year', y='Yield', hue='Country', style='Country', size='Yield', sizes=(20, 200), legend='brief')
    plt.title("Yield Over Time by Country")
    plt.xlabel("Year")
    plt.ylabel("Yield (Megatons)")
    st.pyplot(plt)
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=filtered_data, x='Year', y='Yield')
    plt.title("Nuclear Yield Over Time")
    plt.ylabel("Yield (Megatons)")
    plt.xlabel("Year")
    st.pyplot(plt)
    plt.figure(figsize=(10, 6))
    sns.histplot(data=filtered_data, x='Yield', bins=30, color='red')
    plt.title("Distribution of Nuclear Yields")
    plt.xlabel("Yield (Megatons)")
    plt.ylabel("Frequency")
    st.pyplot(plt)
    view_state = pdk.ViewState(latitude=data['Latitude'].mean(), longitude=data['Longitude'].mean(), zoom=3)
    layer = pdk.Layer("ScatterplotLayer", data=filtered_data, get_position=["Longitude", "Latitude"], get_color="[200, 30, 0, 160]", get_radius=100000, pickable=True, auto_highlight=True)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Country}: Yield {Yield}, Year {Year}"}))

# [DA3] Top largest values of a column
with tab4:
    st.title("Top N Nuclear Explosions by Yield")
    sorted_data = data.nlargest(top_n, 'Yield').reset_index(drop=True)
    st.table(sorted_data[['Country', 'Year', 'Yield']])
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Yield', y='Country', hue='Country', data=sorted_data, palette='viridis', legend=False)
    plt.title("Top Nuclear Explosions by Yield")
    plt.xlabel("Yield (Megatons)")
    plt.ylabel("Country")
    st.pyplot(plt)
