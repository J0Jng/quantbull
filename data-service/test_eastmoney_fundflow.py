"""东方财富资金流向接口测试脚本"""
import os
import requests

BASE_URL = os.getenv("FUND_FLOW_BASE_URL", "http://localhost:8000/api/fundflow")


def test_market():
    resp = requests.get(f"{BASE_URL}/market", params={"market": "hs"})
    data = resp.json()
    print("market status:", data.get("code"), data.get("message"))
    payload = data.get("data") or {}
    print("market as_of:", payload.get("as_of"))
    items = payload.get("items", [])
    print("market items:", items[:3])


def test_sectors():
    resp = requests.get(f"{BASE_URL}/sectors", params={"type": "industry", "page": 1, "page_size": 10})
    data = resp.json()
    print("sectors status:", data.get("code"), data.get("message"))
    payload = data.get("data") or {}
    print("sectors as_of:", payload.get("as_of"))
    items = payload.get("items", [])
    print("sectors items:", items[:3])


def test_stocks():
    resp = requests.get(f"{BASE_URL}/stocks", params={"market": "all", "stat": 1, "page": 1, "page_size": 10})
    data = resp.json()
    print("stocks status:", data.get("code"), data.get("message"))
    payload = data.get("data") or {}
    print("stocks as_of:", payload.get("as_of"))
    items = payload.get("items", [])
    print("stocks items:", items[:3])


if __name__ == "__main__":
    test_market()
    test_sectors()
    test_stocks()
