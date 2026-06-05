import pandas as pd
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from analyzer import load_and_prepare, detect_data_months

# 模拟：文件名202606，数据反馈日期全在2025-06
data = {
    "反馈日期": ["2025-06-01", "2025-06-05", "2025-06-10"],
    "首次时间": ["2020-01-01"] * 3,
    "型号": ["X1"] * 3,
    "盖机/整机": ["盖机"] * 3,
    "配件": ["配件A"] * 3,
    "保内/保外": ["保内"] * 3,
    "客户": ["客户A"] * 3,
    "部品费": [10] * 3,
    "运费": [5] * 3,
    "师傅费用": [20] * 3,
}
df_test = pd.DataFrame(data)

tmp = "c:/Users/DELL/WorkBuddy/20260521102755/uploads/202606test.xlsx"
df_test.to_excel(tmp, index=False)

df, year, month, title = load_and_prepare(tmp)
print(f"load_and_prepare 返回: {year}年{month}月")
print(f"标准化日期: {df['标准化日期'].tolist()[:3]}")
detected = detect_data_months(df)
print(f"detect_data_months: {detected}")
if len(detected) == 1:
    y, m = detected[0]
    print(f">>> 修正后应归类到: {y}年{m}月 >>>")
else:
    print(">>> 无有效日期，回退到文件名月份 >>>")
