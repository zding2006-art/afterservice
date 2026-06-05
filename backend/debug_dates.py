import pandas as pd
import sys
sys.path.insert(0, '.')
from analyzer import load_and_prepare, detect_data_months

filepath = r'c:\Users\DELL\WorkBuddy\20260521102755\backend\uploads\TEST_202504_202509_合并.xlsx'
try:
    df, year, month, title = load_and_prepare(filepath)
    print(f"Parsed from filename: year={year}, month={month}")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)[:15]}")
    print(f"标准化日期_dt sample: {df['标准化日期_dt'].dropna().head(10).tolist()}")
    print(f"标准化日期_dt null count: {df['标准化日期_dt'].isna().sum()} / {len(df)}")
    
    detected = detect_data_months(df)
    print(f"Detected months: {detected}")
except Exception as e:
    import traceback
    traceback.print_exc()
