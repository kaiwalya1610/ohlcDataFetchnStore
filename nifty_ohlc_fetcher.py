import yfinance as yf
from datetime import datetime, timedelta
import os
import pytz
import time
import pandas as pd

class StockDataFetcher:
    def __init__(self, output_folder="nifty_500_data"):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        self.symbols = self._load_all_symbols()

    def _load_symbols_from_file(self, file_path, exchange_name, suffix=""):
        """Load stock symbols from file and return list of tuples."""
        try:
            with open(file_path, 'r') as f:
                symbols = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if symbols:
                return [(f"{s}{suffix}", exchange_name) for s in symbols]
            return []
                
        except FileNotFoundError:
            return []

    def _load_all_symbols(self):
        """Load symbols from all configured sources."""
        nifty_symbols = self._load_symbols_from_file("nifty_500_symbols.txt", "NSE", suffix=".NS")
        sp500_symbols = self._load_symbols_from_file("sp500_symbols.txt", "SnP")
        return nifty_symbols + sp500_symbols

    def fetch_ohlc_data(self, ticker_obj, start_date_str, end_date_str):
        try:
            if start_date_str == end_date_str:
                start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_dt_for_fetch = (start_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                ohlc_data = ticker_obj.history(start=start_date_str, end=end_dt_for_fetch, interval="1m")
            else:
                ohlc_data = ticker_obj.history(start=start_date_str, end=end_date_str, interval="1m")

            if ohlc_data.empty:
                return None
            
            # Convert timezone based on exchange
            if ticker_obj.ticker.endswith('.NS'):
                if ohlc_data.index.tz is None:
                    ohlc_data.index = ohlc_data.index.tz_localize("Asia/Kolkata")
                else:
                    ohlc_data.index = ohlc_data.index.tz_convert("Asia/Kolkata")
            else:
                if ohlc_data.index.tz is None:
                    ohlc_data.index = ohlc_data.index.tz_localize("America/New_York")
                else:
                    ohlc_data.index = ohlc_data.index.tz_convert("America/New_York")
            return ohlc_data
        except:
            return None

    # ------------------------------------------------------------
    # Utility: sanitize parts of filenames to avoid illegal chars
    # ------------------------------------------------------------
    def _sanitize_filename_component(self, text: str) -> str:
        """Replace characters that can break filenames except colon (Linux)."""
        sanitized = text.replace("/", "-").strip()
        return sanitized

    def run(self, past_days=0):
        print(f"🚀 Processing {len(self.symbols)} symbols...")
        
        base_date_for_run = datetime.now()
        batch_size = 20
        symbol_batches = [self.symbols[i:i + batch_size] for i in range(0, len(self.symbols), batch_size)]

        for i, batch_of_symbols in enumerate(symbol_batches):
            print(f"Batch {i+1}/{len(symbol_batches)}")
            
            if i > 0:
                time.sleep(5)

            for symbol, exchange in batch_of_symbols:
                effective_ref_date = base_date_for_run - timedelta(days=1) if exchange == "SnP" else base_date_for_run
                target_date_for_fetch = effective_ref_date - timedelta(days=past_days)
                symbol_start_date_str = target_date_for_fetch.strftime('%Y-%m-%d')
                symbol_end_date_str = symbol_start_date_str 

                ticker_obj = yf.Ticker(symbol)

                # Fetch and save OHLC data only
                ohlc_data = self.fetch_ohlc_data(ticker_obj, symbol_start_date_str, symbol_end_date_str)
                if ohlc_data is not None:
                    ohlc_data['stock_exchange'] = exchange
                    filename_symbol = self._sanitize_filename_component(symbol)
                    ohlc_file_path = os.path.join(self.output_folder, f"{filename_symbol}_daily_ohlc.csv")
                    ohlc_data.to_csv(ohlc_file_path)

                time.sleep(1)

        print("✅ Processing complete!")

if __name__ == "__main__":
    fetcher = StockDataFetcher()
    fetcher.run(past_days=0)
