import requests, os, json
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
url = 'http://localhost:5859/api/upload'
filepath = r'c:\Users\DELL\WorkBuddy\20260521102755\backend\uploads\TEST_202504_202509_合并.xlsx'
with open(filepath, 'rb') as f:
    r = requests.post(url, files={'file': ('test.xlsx', f)}, proxies={'http': None, 'https': None})
d = r.json()
print('is_multi_month:', d.get('is_multi_month'))
print('total_months:', d.get('total_months_detected'))
print('saved:', d.get('saved_months'))
print('skipped:', d.get('skipped_months'))
print('summary month_label:', d.get('summary',{}).get('month_label'))
print('summary records:', d.get('summary',{}).get('total_records'))
for md in (d.get('month_details') or []):
    print(f"  {md['month_label']}: {md['record_count']} records, cost=¥{md['summary']['total_cost']:,.0f}")
if d.get('error'):
    print('ERROR:', d['error'])
