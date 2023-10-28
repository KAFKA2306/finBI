import os
import pandas as pd
import yfinance as yf
import pickle
from fredapi import Fred
import streamlit as st
from  categories import CATEGORIES, FRED_CATEGORIES, FRED_API_KEY,DATA_DIR,FILE_PATHS

fred = Fred(api_key=FRED_API_KEY)

def save_to_pickle(data_dict, source):
    file_path = os.path.join(DATA_DIR, f"{source}.pkl")
    with open(file_path, 'wb') as f:
        pickle.dump(data_dict, f)

def load_from_pickle(source):
    file_path = os.path.join(DATA_DIR, f"{source}.pkl")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return {}

def fetch_data(identifier, source):
    if source == "stock":
        return yf.Ticker(identifier).history(period="10y")['Close']
    elif source == "fred":
        return fred.get_series(identifier)

def fetch_or_load_data(identifier, source):
    data_dict = load_from_pickle(source)
    
    if identifier in data_dict:
        return data_dict[identifier]
    
    data = fetch_data(identifier, source)
    
    if data is not None:
        data_dict[identifier] = data
        save_to_pickle(data_dict, source)
        
    return data

def main():
    st.title("Efficient Financial Data Dashboard using Source-Based Pickle Files")

    # Combine both category lists for selection
    all_categories = list(CATEGORIES.keys()) + list(FRED_CATEGORIES.keys())
    selected_category = st.selectbox("Select a Category:", all_categories)

    # Combine both ticker and series lists for selection
    options_list = CATEGORIES.get(selected_category, []) + FRED_CATEGORIES.get(selected_category, [])
    selected_identifier = st.selectbox("Select a Ticker/Series:", options_list)

    # Determine the source based on the category
    source = "stock" if selected_category in CATEGORIES else "fred"

    data = fetch_or_load_data(selected_identifier, source)
    st.line_chart(data)
    
if __name__ == "__main__":
    main()



def load_and_merge_data(file_paths):
    merged_df = pd.DataFrame()
    for file_path in file_paths:
        data_dict = pd.read_pickle(file_path)
        for key, series_data in data_dict.items():
            merged_df[key] = series_data
    return merged_df

def main():
    # Streamlit title
    st.title("Select Time Series Data")

    # Load and merge data
    merged_data = load_and_merge_data([FILE_PATHS['stock'], FILE_PATHS['fred']])
    merged_data.to_csv(FILE_PATHS['stock_fred_csv'])
    merged_data.to_pickle(FILE_PATHS['stock_fred_pkl'])

    # Get column names and allow selection in Streamlit
    all_columns = merged_data.columns.tolist()
    selected_columns = st.multiselect("Select columns to display", all_columns, default=['VOO', 'VIG', 'TLT'])
    if selected_columns:
        st.dataframe(merged_data[selected_columns])
        #st.dataframe(pd.read_pickle(FILE_PATHS['stock']))

if __name__ == "__main__":
    main()
