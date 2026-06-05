import pandas as pd
import sys
sys.path.insert(0, '.')
from analyzer import load_and_prepare, detect_data_months, split_by_month, run_all_analysis

# 模拟一个多月数据：手动创建包含4月和9月数据的 DataFrame
import numpy as np
from datetime import datetime

# 用实际 Excel 文件来测试 —— 但用 Python 直接读两个文件并统一日期格式
f1 = r'c:\Users\DELL\WorkBuddy\20260521102755\backend\uploads\202504售后数据.xlsx'
f2 = r'c:\Users\DELL\WorkBuddy\20260521102755\backend\uploads\202509售后配件记录.xlsx'

df1 = pd.read_excel(f1)
df2 = pd.read_excel(f2)

# 重要：把两个文件的日期都统一转为 datetime
col1 = df1.columns[0]
col2 = df2.columns[0]

# df1 的日期格式可能是 datetime 或数字，统一处理
def fix_date(v, y, m):
    if pd.isna(v): return v
    if isinstance(v, (datetime, pd.Timestamp)): return v
    if isinstance(v, (int, float)):
        return pd.Timestamp(f'{y}-{m:02d}-{int(float(v)):02d}')
    return v

df1[col1] = df1[col1].apply(lambda v: fix_date(v, 2025, 4))
df2[col2] = df2[col2].apply(lambda v: fix_date(v, 2025, 9))

# 统一列名以便合并
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

merged = pd.concat([df1, df2], ignore_index=True)
print(f"Merged rows: {len(merged)}")
print(f"Unique dates (head 5 + tail 5): {merged.iloc[:,0].head(5).tolist() + merged.iloc[:,0].tail(5).tolist()}")

# 保存为 Excel
out = r'c:\Users\DELL\WorkBuddy\20260521102755\backend\uploads\TEST_MULTI_MONTH_v2.xlsx'
merged.to_excel(out, index=False)

# 重新读取测试
df, year, month, title = load_and_prepare(out)
print(f"\nload_and_prepare: year={year}, month={month}")
print(f"标准化日期_dt sample (first 3): {df['标准化日期_dt'].head(3).tolist()}")
print(f"标准化日期_dt sample (last 3): {df['标准化日期_dt'].tail(3).tolist()}")
print(f"标准化日期_dt null: {df['标准化日期_dt'].isna().sum()}/{len(df)}")

detected = detect_data_months(df)
print(f"\nDetected months: {detected}")

if len(detected) > 1:
    groups = split_by_month(df, year, month)
    print(f"Month groups: {[(k, len(v)) for k,v in groups.items()]}")
else:
    print("Only 1 month detected")

# 完整运行
_, results, summary, is_multi, details = run_all_analysis(out)
print(f"\nrun_all_analysis: is_multi={is_multi}")
if details:
    for md in details:
        print(f"  {md['month_label']}: {md['record_count']} records, cost={md['summary']['total_cost']:,.0f}")
