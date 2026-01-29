import json
import urllib.request
import urllib.parse
import threading

URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

CANDIDATES = [
    "RPT_DAILYBILLBOARD_DETAILS",
    "RPT_DAILYBILLBOARD_DETAILSNEW",
    "RPT_LHB_BOARD_REC_DAILY",
    "RPT_ORGANIZATION_TRADE_DETAILSNEW", 
    "RPT_BILLBOARD_TRADEALLNEW"
]

def check(report_name):
    params = {
        "reportName": report_name,
        "columns": "ALL",
        "pageNumber": 1,
        "pageSize": 5,
        "sortColumns": "TRADE_DATE",
        "sortTypes": "-1",
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{URL}?{query_string}"
    
    try:
        with urllib.request.urlopen(full_url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("result"):
                    items = data["result"]["data"]
                    if items:
                        print(f"[SUCCESS] {report_name}: Found {len(items)} items. Latest Date: {items[0].get('TRADE_DATE')}")
                        print(f"ALL Keys: {list(items[0].keys())}")
                    else:
                        print(f"[EMPTY] {report_name}: Result format ok but no data.")
                else:
                    print(f"[FAIL] {report_name}: {data.get('message', 'Unknown error')}")
            else:
                 print(f"[HTTP ERROR] {report_name}: {response.status}")
    except Exception as e:
        print(f"[ERROR] {report_name}: {e}")

def main():
    threads = []
    for name in CANDIDATES:
        t = threading.Thread(target=check, args=(name,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
