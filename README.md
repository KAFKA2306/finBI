---

## Overview
This Streamlit application provides a user-friendly interface for analyzing financial and economic data across various categories. It fetches stock data as well as economic data from the FRED (Federal Reserve Economic Data) database, offering a comprehensive view of financial markets.

## Features

- **User-friendly Interface**: Features an easy-to-navigate sidebar for selecting data categories or series.
- **Data Caching**: Efficiently fetches and stores data using Pickle files, reducing redundant API calls and improving loading times.
- **Interactive Visualization**: Leverages Streamlit and Plotly charts for interactive data visualization, offering insightful views into the data.
- **Extensive Data Sources**: Integrates multiple data sources including Yahoo Finance, FRED, SimFin, and Finnhub, for a wide range of financial data.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/KAFKA2306/finBI.git
```
2. Obtain the necessary API keys for FRED_API_KEY, SIMFIN_API_KEY, ALPHA_VANTAGE_API_KEY, FinancialModelingPrep_API_KEY, FINNHUB_API_KEY, and update them in the `categories.py` file.

## How to Run

- Run the batch file:
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

## Contributing

If you come across any bugs, or if you have additional features you think would be nice to have, feel free to open a GitHub issue. Contributions are always welcome.

---




---

## 株価と経済データ分析ウェブアプリ

このPythonスクリプトは、異なるデータソースから株価や経済データを取得し、それらのデータを分析し、Streamlitを使用して表示するものです。

### 1. **インポートと設定:**
コードの最初の部分で、必要なライブラリと設定を準備します。

```python
import os
import pandas as pd
import yfinance as yf
import pickle
from fredapi import Fred
import simfin as sf
from simfin.names import *
import streamlit as st
import requests
from categories import (
    CATEGORIES, FRED_CATEGORIES, FRED_API_KEY, DATA_DIR, 
    SIMFIN_API_KEY, ALPHA_VANTAGE_API_KEY, INDIVIDUAL_STOCKS, 
    FinancialModelingPrep_API_KEY, FINNHUB_API_KEY
)

fred = Fred(api_key=FRED_API_KEY)
sf.set_api_key(SIMFIN_API_KEY)
sf.set_data_dir(DATA_DIR)

DEFAULT_TICKERS = ['MSFT', 'AAPL', 'AMZN']

```

### 2. **DataHandlerクラス:**
`DataHandler` クラスはデータの取得と保存を担当します。

```python
class DataHandler:
    # ...
```

- `_get_file_path`, `_save_to_pickle`, `_load_from_pickle`: ファイルパスの生成、データの保存と読み込み。
- `_fetch_data`, `get_data`: 異なるデータソースからデータを取得。
- `process_and_save_simfin_data`, `merge_and_save_data`: データの処理とマージ。

### 3. **StreamlitDisplayクラス:**
`StreamlitDisplay` クラスは、Streamlitウェブアプリでのデータ表示を制御します。

```python
class StreamlitDisplay:
    # ...
```

- `display_chart`, `display_table`, `display_earnings`: チャートやテーブルの表示。
- `select_category_and_tickers`, `display_selected_data`: カテゴリやティッカーの選択と表示。

### 4. **Main Functions:**
各 `main_` 関数は、特定のデータセットと表示タイプに基づいてStreamlitウェブアプリの異なるセクションを制御します。

```python
def main_yf_chart(data_handler, display_handler):
    # ...
def main_yf_table(data_handler, display_handler):
    # ...
def main_simfin(data_handler, display_handler):
    # ...
def main_finnhub(data_handler, display_handler):
    # ...
```

### 5. **メイン実行ブロック:**
`__main__` ブロックで、`DataHandler`と`StreamlitDisplay`のインスタンスを作成し、各 `main_` 関数を呼び出します。

```python
if __name__ == "__main__":
    data_handler = DataHandler()
    display_handler = StreamlitDisplay(data_handler)

    main_yf_chart(data_handler, display_handler)
    main_yf_table(data_handler, display_handler)
    main_simfin(data_handler, display_handler)
    main_finnhub(data_handler, display_handler)

```

