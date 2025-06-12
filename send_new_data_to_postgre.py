#!/usr/bin/env python3
import os
import glob
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import numpy as np
import json
from typing import List, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database config - now loaded from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "sslmode": os.getenv("DB_SSLMODE", "require")
}

def connect_to_db() -> psycopg2.extensions.connection:
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_csv_files(data_dir: str = "nifty_500_data") -> List[str]:
    """Get list of CSV files to process"""
    return glob.glob(os.path.join(data_dir, "*_daily_ohlc.csv"))

def extract_stock_symbol(file_path: str) -> str:
    """Extract stock symbol from filename"""
    base = os.path.basename(file_path)
    return base.replace('_daily_ohlc.csv', '')

def clean_dataframe(df: pd.DataFrame, stock_symbol: str) -> pd.DataFrame:
    """Transform raw CSV data to match database schema"""
    # Rename columns
    df.rename(columns={
        'Datetime': 'date_time',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume',
        'Dividends': 'dividends',
        'Stock Splits': 'stock_splits'
    }, inplace=True)

    # Add missing columns with defaults
    for col in ['dividends', 'stock_splits']:
        if col not in df.columns:
            df[col] = 0.0
    
    if 'stock_exchange' not in df.columns:
        df['stock_exchange'] = None

    # Convert datetime and add stock symbol
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['stock_symbol'] = stock_symbol
    
    # Return columns in correct order
    return df[['stock_symbol', 'date_time', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits', 'stock_exchange']]

def prepare_data_for_insert(df: pd.DataFrame) -> List[List]:
    """Convert DataFrame to list format for database insertion"""
    records = df.to_records(index=False)
    return [[val.item() if isinstance(val, np.generic) else val for val in row] for row in records]

def insert_stock_data(cursor, data: List[List]) -> None:
    """Insert data into stock_data table"""
    insert_query = """
    INSERT INTO stock_data (stock_symbol, date_time, open, high, low, close, volume, dividends, stock_splits, stock_exchange)
    VALUES %s
    ON CONFLICT (stock_symbol, date_time) DO NOTHING;
    """
    execute_values(cursor, insert_query, data)

def process_single_file(file_path: str, cursor) -> bool:
    """Process a single CSV file and insert its data"""
    base_symbol = extract_stock_symbol(file_path)
    
    # Try to load the descriptive symbol from the corresponding JSON file
    info_file_path = file_path.replace('_daily_ohlc.csv', '_info.json')
    stock_symbol_to_use = base_symbol  # Default to base symbol

    if os.path.exists(info_file_path):
        try:
            with open(info_file_path, 'r') as f:
                info_data = json.load(f)
                # Use the descriptive symbol if it exists, otherwise stick with the base symbol
                stock_symbol_to_use = info_data.get('descriptive_symbol', base_symbol)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"⚠️  Could not read or parse {info_file_path}, falling back to base symbol '{base_symbol}'.")
            pass # Keep using base_symbol as fallback
    
    # Read CSV
    df = pd.read_csv(file_path)
    if df.empty:
        print(f"Empty file: {file_path}")
        return False
    
    # Transform data
    cleaned_df = clean_dataframe(df, stock_symbol_to_use)
    data = prepare_data_for_insert(cleaned_df)
    
    # Insert data
    insert_stock_data(cursor, data)
    print(f"✅ Inserted data from {file_path} as '{stock_symbol_to_use}'")
    return True

def main():
    """Main pipeline function"""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        csv_files = get_csv_files()
        processed_count = 0
        
        for file_path in csv_files:
            if process_single_file(file_path, cursor):
                processed_count += 1
            conn.commit()
        
        print(f"🎉 Successfully processed {processed_count}/{len(csv_files)} files")
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
