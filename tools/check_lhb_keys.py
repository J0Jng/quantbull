import httpx
import asyncio

async def main():
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    # Using the report name found in code: RPT_ORGANIZATION_TRADE_DETAILSNEW
    # Or RPT_LHB_LIST
    # The code prefers RPT_ORGANIZATION_TRADE_DETAILSNEW for "list"
    
    # Let's try to get one day data
    params = {
        "reportName": "RPT_LHB_LIST", # Trying the common one first or RPT_ORGANIZATION_TRADE_DETAILSNEW 
        "columns": "ALL",
        "pageNumber": 1,
        "pageSize": 5,
        "sortColumns": "SECURITY_CODE",
        "sortTypes": 1,
        "filter": "(TRADE_DATE='2025-01-23')" # Using a recent valid trading date
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with httpx.AsyncClient() as client:
        # Try preferred report name first
        params["reportName"] = "RPT_ORGANIZATION_TRADE_DETAILSNEW"
        resp = await client.get(url, params=params, headers=headers)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            if data['result'] and data['result']['data']:
                print("Keys:", data['result']['data'][0].keys())
                print("Sample:", data['result']['data'][0])
            else:
                 print("No data found with RPT_ORGANIZATION_TRADE_DETAILSNEW")
                 
                 # Try fallback
                 params["reportName"] = "RPT_LHB_LIST"
                 resp = await client.get(url, params=params, headers=headers)
                 data = resp.json()
                 if data['result'] and data['result']['data']:
                    print("Keys (RPT_LHB_LIST):", data['result']['data'][0].keys())
        except Exception as e:
            print(e)

if __name__ == "__main__":
    asyncio.run(main())
