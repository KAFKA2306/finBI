# finBI

## Overview

This Streamlit application provides a user-friendly interface for analyzing financial data across various categories. The application not only handles stock data but also economic data from the FRED (Federal Reserve Economic Data) database. 

## Features

- **User-friendly Interface**: Easy-to-navigate sidebar for selecting data categories or series.
- **Data Caching**: Efficiently fetches and stores data using CSV and pkl files, reducing redundant API calls.
- **Interactive Visualization**: Utilizes Plotly charts for interactive data visualization.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/KAFKA2306/finBI.git  
    ```
2. Obtain the FRED and SIMFIN API Key and update it in the categories.py file.

## How to Run

1. Run bat:
    ```bash
    ./KAFKA2306/finBI/blob/main/code/first.bat
    ```

## Dependencies

- Streamlit
- pandas
- yfinance
- fredapi
- Plotly

## Contributing

If you find any bugs, or if you have additional features you think would be nice to have, please do open a GitHub issue. Contributions are welcome.
