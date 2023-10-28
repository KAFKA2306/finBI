
FRED_API_KEY = 'yours'

# File Paths
DATA_DIR = "./../data/"
# Define constants for file paths
FILE_PATHS = {
    'stock': "M:\\ML\\Finance\\BI\\data\\stock.pkl",
    'fred': "M:\\ML\\Finance\\BI\\data\\fred.pkl",
    'stock_fred_pkl': "M:\\ML\\Finance\\BI\\data\\stock_fred.pkl",
    'stock_fred_csv': "M:\\ML\\Finance\\BI\\data\\stock_fred.csv"
}

# yfinance
ETF_CATEGORIES = [
    'VOO', 'VIG',  # Standard ETFs
    'TLT', 'IEF', 'AGG',  # Bonds
    'FXE', 'FXY', 'FXB', 'FXA',  # Forex
    'GLD',  # Goods and Commodities
    'TQQQ', 'UPRO', 'TMF', 'TMV', 'CURE', 'SOXL',  # Leveraged ETFs
    'CWEB', 'YINN',  # Country-specific ETFs
    'JPY=X',  # USD/JPY
    'EURJPY=X'  # EUR/JPY
]


INDIVIDUAL_STOCKS = [
    'MSFT', 'AAPL', 'AMZN', 'GOOGL', 'BRK-B', 'JPM',  # US Stocks
    'JNJ', 'PFE', 'MRK', 'UNH',  # Healthcare
    'PG', 'KO', 'PEP', 'MCD',  # Consumer Goods
    'COIN'  # Crypto Related
]

CATEGORIES = {
    'ETF': ETF_CATEGORIES,
    'Individual Stocks': INDIVIDUAL_STOCKS
}

# Economic Indicators
ECONOMIC_INDICATORS = ['GDP', 'CPIAUCNS', 'UNRATE', 'PAYEMS', 'INDPRO', 'CIVPART', 'HOUST']

# Financial Markets
FINANCIAL_MARKETS = ['FEDFUNDS', 'GS10', 'GS1', 'AAA', 'BAA', 'SP500', 'NASDAQCOM', 'DJIA', 'WILL5000INDFC', 'VIXCLS', 'TEDRATE']

# Exchange and Commodities
EXCHANGE_AND_COMMODITIES = ['DTB3', 'DTB6', 'DTB1YR', 'AAA10Y', 'BAA10Y', 'MORTGAGE30US', 'MORTGAGE15US', 'WTISPLC', 'GASREGW', 'CPILFESL', 'PCE', 'CUSR0000SAC', 'RRSFS']

FRED_CATEGORIES = {
    'Economic Indicators': ECONOMIC_INDICATORS,
    'Financial Markets': FINANCIAL_MARKETS,
    'Exchange and Commodities': EXCHANGE_AND_COMMODITIES
}
