import os
import pandas as pd
import yfinance as yf
import pickle
from fredapi import Fred
import simfin as sf
from simfin.names import *
import streamlit as st
import requests
import plotly.graph_objects as go
from categories import (
    CATEGORIES, FRED_CATEGORIES, FRED_API_KEY, DATA_DIR, 
    SIMFIN_API_KEY, ALPHA_VANTAGE_API_KEY, INDIVIDUAL_STOCKS, 
    FinancialModelingPrep_API_KEY, FINNHUB_API_KEY
)

fred = Fred(api_key=FRED_API_KEY)
sf.set_api_key(SIMFIN_API_KEY)
sf.set_data_dir(DATA_DIR)

DEFAULT_TICKERS = ['MSFT', 'AAPL', 'AMZN']  # ここにデフォルトのティッカーをリストとして提供します

st.title("KaFin")

# YahooFinance
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

def save_data():
    all_categories = list(CATEGORIES.keys()) + list(FRED_CATEGORIES.keys())
    for category in all_categories:
        options_list = CATEGORIES.get(category, []) + FRED_CATEGORIES.get(category, [])
        for identifier in options_list:
            source = "stock" if category in CATEGORIES else "fred"
            fetch_or_load_data(identifier, source)

def plot_data():
    st.title("Stock and FRED")

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
    save_data()
    plot_data()
    
# YahooFinance_Table
def load_and_merge_data(file_paths):
    merged_df = pd.DataFrame()
    for file_path in file_paths:
        data_dict = pd.read_pickle(file_path)
        for key, series_data in data_dict.items():
            merged_df[key] = series_data
    return merged_df

def main():
    # Streamlit title
    st.title("Stock and FRED Table")

    # Load and merge data
    merged_data = load_and_merge_data([f"{DATA_DIR}/stock.pkl",f"{DATA_DIR}/fred.pkl"])
    merged_data.to_pickle(f"{DATA_DIR}/stock_fred.pkl")

    # Get column names and allow selection in Streamlit
    all_columns = merged_data.columns.tolist()
    selected_columns = st.multiselect("Select columns to display", all_columns, default=['VOO', 'VIG', 'TLT'])
    if selected_columns:
        st.dataframe(merged_data[selected_columns])
        #st.dataframe(pd.read_pickle(FILE_PATHS['stock']))

if __name__ == "__main__":
    main()






# Stock-FX
st.title("FX")
stocks_list = pd.read_pickle(f"{DATA_DIR}/stock.pkl")
stocks_df = pd.DataFrame(stocks_list).resample("D").mean()
stocks_df['EUR=X'] = 1 / (stocks_df['EURJPY=X'] / stocks_df['JPY=X'])
FX = stocks_df[['JPY=X','EUR=X']]

stocks_dollars = stocks_df[['VOO', 'VT', 'QQQ', 'VIG', 'TLT', 'AGG', 'GLD']]
stocks_yen = stocks_dollars.multiply(FX['JPY=X'], axis=0)
stocks_euro = stocks_dollars.multiply(FX['EUR=X'], axis=0)

# Create an empty dictionary to store the ticker DataFrames
ticker_dfs = {}

for ticker in stocks_dollars.columns:
    # Create a DataFrame for each ticker with USD, JPY, and EUR values
    ticker_dfs[ticker] = pd.DataFrame({
        f"{ticker}_USD": stocks_dollars[ticker],
        f"{ticker}_JPY": stocks_yen[ticker],
        f"{ticker}_EUR": stocks_euro[ticker]
    })

# Concatenate all the ticker DataFrames along with the FX DataFrame into a single DataFrame
stocks_FX = pd.concat([*ticker_dfs.values(), FX], axis=1)


# Streamlit UI
unique_tickers = stocks_dollars.columns.tolist()
default_selected = ['VOO']
all_options = unique_tickers + FX.columns.tolist()

selected_tickers = st.multiselect(
    'Select Tickers to Plot',
    options=all_options,  # Use the combined list here
    default=default_selected
)

selected_currencies = st.multiselect(
    'Select Currencies',
    options=FX.columns.tolist()+['USD'],
    default=FX.columns.tolist()+['USD']
)

def get_matching_columns(selected_tickers, selected_currencies):
    matching_columns = []
    for ticker in selected_tickers:
        for currency in selected_currencies:
            if currency == 'USD':
                matching_columns.append(f"{ticker}_USD")
            else:
                currency_suffix = currency.replace('=X', '')
                matching_columns.extend([col for col in stocks_FX.columns if col.startswith(f"{ticker}_") and col.endswith(currency_suffix)])
    return matching_columns


# Plot
def multi_yaxis_plot(df):
    fig = go.Figure()
    for idx, column in enumerate(df.columns, 1):
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                name=column,
                yaxis=f'y{idx}' if idx > 1 else 'y'
            )
        )
    yaxis_dict = {
        f'yaxis{idx}' if idx > 1 else 'yaxis': dict(
            title=f'yaxis {idx} title',
            overlaying='y' if idx > 1 else None,
            side='right' if idx % 2 == 0 else 'left'
        )
        for idx in range(1, len(df.columns) + 1)
    }
    fig.update_layout(**yaxis_dict)
    st.plotly_chart(fig)


matching_columns = get_matching_columns(selected_tickers, selected_currencies)  # updated line
multi_yaxis_plot(stocks_FX[matching_columns])





# SIMFIN
REVENUE, NET_INCOME, DEFAULT_TICKERS = 'Revenue', 'Net Income', ['MSFT', 'AAPL', 'AMZN']

def fetch_or_load_data(variant='quarterly', market='us'):
    path = f"simfin_{variant}_{market}.pkl"
    try:
        with open(path, 'rb') as f:
            df_income = pickle.load(f)
    except:
        df_income = sf.load_income(variant=variant, market=market)
        with open(path, 'wb') as f:
            pickle.dump(df_income, f)
    return df_income

def prepare_data(df_income):
    df = df_income.reset_index()
    df['Report Date'] = pd.to_datetime(df['Report Date'])  # 確実に日付型に変換
    # RevenueとNet Incomeのデータフレームを作成
    df_revenue = df.pivot(index='Report Date', columns='Ticker', values=REVENUE).resample('3M').sum()
    df_net_income = df.pivot(index='Report Date', columns='Ticker', values=NET_INCOME).resample('3M').sum()
    return df_revenue, df_net_income


def main():
    st.title("Earnings")

    df_revenue, df_net_income = prepare_data(fetch_or_load_data())
    tickers = df_revenue.columns.tolist()

    category = st.selectbox("Select Category", ['Revenue', 'Net Income'])
    df = df_revenue if category == 'Revenue' else df_net_income
    st.line_chart(df[st.multiselect("Select Tickers", tickers, default=DEFAULT_TICKERS)])

    st.title("Earnings Table")
    selected_tickers = st.multiselect("Select tickers", tickers, default=DEFAULT_TICKERS)
    if selected_tickers:
        for title, df in zip(["Revenue", "Net Income"], [df_revenue, df_net_income]):
            st.write(title)
            st.dataframe(df[selected_tickers])

if __name__ == "__main__":
    main()
fetch_or_load_data(variant='quarterly', market='us')







# EARNINGS FINNHUB
COMPANIES = ["GOOGL", "AAPL", "META", "AMZN", "MSFT"]
FILE_NAME = "earnings_finnhub.pkl"
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

def get_finnhub_earnings(symbol, api_key):
    url = f"https://finnhub.io/api/v1/stock/earnings?symbol={symbol}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
    except requests.RequestException as e:
        print(f"Failed to fetch earnings data for {symbol}: {e}")
        return None
    
    data = response.json()
    df = pd.DataFrame(data)
    return df

def save_earnings_data(companies, data_dir, api_key):
    all_data = []
    for company in companies:
        file_path = os.path.join(data_dir, f"{company}_historical_quarterly_earnings.pkl")
        if os.path.exists(file_path):
            df = pd.read_pickle(file_path)
        else:
            df = get_finnhub_earnings(company, api_key)
            if df is not None:
                df.to_pickle(file_path)
                print(f"Data saved to {file_path}")
        if df is not None:
            df['Company'] = company  # Add a 'Company' column
            all_data.append(df)
    
    # Combine all data into one DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save all data back to disk
    combined_df.to_pickle(FILE_PATH)
    print(f"Data saved to {FILE_PATH}")

def load_and_organize_data(file_path):
    data = pd.read_pickle(file_path)
    data['period'] = pd.to_datetime(data['period'])  # Convert 'period' to datetime here
    data.set_index('period', inplace=True)  # Set 'period' as the index here
    
    # Use pivot_table instead of pivot
    pivot_data = data.pivot_table(index='period', columns='Company', values=['actual', 'estimate', 'surprisePercent'])
    
    # Swap the levels of the columns
    pivot_data.columns = pivot_data.columns.swaplevel(0, 1)
    pivot_data.sort_index(axis=1, level=0, inplace=True)
    
    return pivot_data


def main():
    st.title("Earnings Surprise")

    # Save and organize data
    save_earnings_data(COMPANIES, DATA_DIR, FINNHUB_API_KEY)
    organized_data = load_and_organize_data(FILE_PATH)

    # Multiselect for companies and items
    selected_companies = st.multiselect(
        "Select Companies", options=COMPANIES, default=["MSFT"]
    )
    selected_items = st.multiselect(
        "Select Items", options=['actual', 'estimate'], default=['actual', 'estimate']
    )

    # Filter out 'surprisePercent' from selected_items
    selected_items = [item for item in selected_items if item != 'surprisePercent']

    # Plotting
    if selected_items:  # Check if there are any items selected
        # Get the data for the selected items and companies
        filtered_data = organized_data.loc(axis=1)[selected_companies, selected_items]
        
        # For 'actual' and 'estimate' plot together
        if 'actual' in selected_items and 'estimate' in selected_items:
            actual_estimate_data = filtered_data.xs('actual', level=1, axis=1).join(
                filtered_data.xs('estimate', level=1, axis=1), lsuffix='_actual', rsuffix='_estimate')
            st.line_chart(actual_estimate_data, use_container_width=True)

            st.write(f"Data Table")
            st.dataframe(actual_estimate_data)
        else:
            for item in selected_items:
                st.write(f"{item} plot")
                item_data = filtered_data.xs(item, level=1, axis=1)
                st.line_chart(item_data, use_container_width=True)

                st.write(f"{item} table")
                st.dataframe(item_data)

if __name__ == "__main__":
    main()









# AlphaVintage
FILE_NAME = "earnings_av2.pick"
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

def fetch_and_save_data():
    error_messages = []  # Create an empty list to collect error messages

    def fetch_quarterly_income_statement(symbol):
        url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        r = requests.get(url)
        data = r.json()
        
        if "quarterlyReports" in data:
            df = pd.DataFrame(data["quarterlyReports"])
            df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])
            df.set_index('fiscalDateEnding', inplace=True)
            df.sort_index(inplace=True)
            return df[['totalRevenue', 'netIncome']]
        # else:
        #     error_messages.append(f"Error fetching data for {symbol}.")  # Append the error message
        #     return None
    
    if os.path.exists(FILE_PATH):
        all_data = pd.read_pickle(FILE_PATH)
    else:
        all_data = {}
    
    for stock in INDIVIDUAL_STOCKS:
        if stock not in all_data:
            df = fetch_quarterly_income_statement(stock)
            if df is not None:
                all_data[stock] = df
    
    pd.to_pickle(all_data, FILE_PATH)

    if error_messages:  # Check if there are any error messages
        st.warning("Some errors occurred while fetching data.")
        for message in error_messages:
            st.write(message)
            
    return all_data


def main():
    st.title("Earnings AlphaVantage")

    all_data = fetch_and_save_data()

    selected_companies = st.multiselect("Select Companies", list(all_data.keys()))

    category = st.selectbox("Choose a category", ["totalRevenue", "netIncome"])

    for company in selected_companies:
        df = all_data[company]
        st.line_chart(df[category])
        st.write(f"{company} Quarterly Earnings Table")
        st.dataframe(df)

if __name__ == "__main__":
    main()