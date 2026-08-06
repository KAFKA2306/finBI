"""Static dataset identifiers retained from the legacy prototype.

Credentials and machine-specific paths do not belong in this module. Runtime
configuration is defined in ``settings.py`` and loaded from environment variables.
"""

ETF_CATEGORIES = [
    "VOO", "VIG", "TLT", "IEF", "AGG", "FXE", "FXY", "FXB", "FXA", "GLD",
    "TQQQ", "UPRO", "TMF", "TMV", "CURE", "SOXL", "CWEB", "YINN", "JPY=X",
    "EURJPY=X",
]

INDIVIDUAL_STOCKS = [
    "MSFT", "AAPL", "AMZN", "GOOGL", "BRK-B", "JPM", "JNJ", "PFE", "MRK",
    "UNH", "PG", "KO", "PEP", "MCD", "COIN",
]

CATEGORIES = {"ETF": ETF_CATEGORIES, "Individual Stocks": INDIVIDUAL_STOCKS}

ECONOMIC_INDICATORS = ["GDP", "CPIAUCNS", "UNRATE", "PAYEMS", "INDPRO", "CIVPART", "HOUST"]
FINANCIAL_MARKETS = [
    "FEDFUNDS", "GS10", "GS1", "AAA", "BAA", "SP500", "NASDAQCOM", "DJIA",
    "WILL5000INDFC", "VIXCLS", "TEDRATE",
]
EXCHANGE_AND_COMMODITIES = [
    "DTB3", "DTB6", "DTB1YR", "AAA10Y", "BAA10Y", "MORTGAGE30US",
    "MORTGAGE15US", "WTISPLC", "GASREGW", "CPILFESL", "PCE", "CUSR0000SAC",
    "RRSFS",
]
FRED_CATEGORIES = {
    "Economic Indicators": ECONOMIC_INDICATORS,
    "Financial Markets": FINANCIAL_MARKETS,
    "Exchange and Commodities": EXCHANGE_AND_COMMODITIES,
}
