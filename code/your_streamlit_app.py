import os
import pandas as pd
import yfinance as yf
import streamlit as st
from categories import CATEGORIES

DATA_DIR = "./../data/"

def save_data(ticker, data, data_type, data_dir):
    file_path = f"{data_dir}{ticker}_{data_type}.csv"
    data.to_csv(file_path)

def fetch_stock_data(ticker, data_dir):
    file_path = f"{data_dir}{ticker}_history.csv"
    
    if os.path.exists(file_path):
        stock_data = pd.read_csv(file_path, index_col=0)
    else:
        stock_data = yf.Ticker(ticker).history(period="1y")
        stock_data.index = stock_data.index.strftime('%Y-%m-%d')
        save_data(ticker, stock_data, "history", data_dir)
        
    return stock_data['Close'].rename(ticker), None

st.title("Multi-Category Stock Data and Earnings")

# Select a category
selected_category = st.selectbox("Select a category:", list(CATEGORIES.keys()))

# Fetch and Plot
for ticker in CATEGORIES[selected_category]:
    new_data, error_msg = fetch_stock_data(ticker, DATA_DIR)
   
    if new_data is not None:
        st.write(f"## {ticker} - Stock Price in {selected_category}")
        st.line_chart(new_data)
