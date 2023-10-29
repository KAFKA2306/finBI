---

## Overview
Dive into the financial realm with this intuitive Streamlit application, your gateway to a wealth of economic and stock market data. With data right from the reputable FRED database and stock market indexes, it’s more than just numbers—it’s the pulse of the financial market at your fingertips.

## Features

- **Ease of Navigation**: Glide through data categories or series with a streamlined sidebar, making your exploration intuitive.
- **Data at Speed**: Through Pickle files, data caching cuts down redundant API calls, ensuring a swift response and reduced loading times.
- **Engaging Visuals**: The marriage of Streamlit and Plotly charts brings forth interactive visualizations, turning data into insights you can almost touch.
- **A Confluence of Sources**: Delve into a broad spectrum of financial data, thanks to integration with Yahoo Finance, FRED, SimFin, and Finnhub.

## Get Started

1. Clone your new financial companion:
```bash
git clone https://github.com/KAFKA2306/finBI.git
```
2. Obtain and fill in your API keys for `FRED_API_KEY`, `SIMFIN_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `FinancialModelingPrep_API_KEY`, `FINNHUB_API_KEY` in the `categories.py` file.

## How to Launch

- Kickstart the application:
```bash
./KAFKA2306/finBI/blob/main/code/first.bat
```

## Dependencies

- Streamlit
- pandas
- yfinance
- fredapi
- Plotly
- requests

## Join the Journey

Stumbled upon a bug or have a feature in mind? Your insights are invaluable. Feel free to open a GitHub issue—let’s refine this financial lens together.

---

---

## Financial and Economic Data Analysis Web App

Dive deep into stock and economic data analysis with this Python script, which fetches, analyzes, and displays data from varied sources using Streamlit.

### 1. **Preparation:**
Set up the stage with necessary libraries and configurations right at the outset.

```python
# Import libraries and configurations
# ...

fred = Fred(api_key=FRED_API_KEY)
sf.set_api_key(SIMFIN_API_KEY)
sf.set_data_dir(DATA_DIR)

DEFAULT_TICKERS = ['MSFT', 'AAPL', 'AMZN']
```

### 2. **DataHandler Class:**
The `DataHandler` class is your data custodian, managing retrieval and storage seamlessly.

```python
class DataHandler:
    # ...
```

- File path creation, data storage, and retrieval functions.
- Data fetching from a variety of sources.

### 3. **StreamlitDisplay Class:**
`StreamlitDisplay` orchestrates data presentation in the Streamlit web app, making it visually appealing and insightful.

```python
class StreamlitDisplay:
    # ...
```

- Functions for displaying charts, tables, and earnings.
- Selection and display of data categories and tickers.

### 4. **Main Functions:**
The `main_` functions control different sections of the Streamlit web app based on specific datasets and display types.

```python
# Controlling different sections of the app
# ...
```

### 5. **Execution Block:**
In the `__main__` block, craft instances of `DataHandler` and `StreamlitDisplay`, and call the `main_` functions to bring the app to life.

```python
if __name__ == "__main__":
    # Creating instances and calling functions
    # ...
```

Make your financial analysis more engaging and insightful with this well-structured, user-friendly application.

---
