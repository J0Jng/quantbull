import json

from services.eastmoney_report_service import EastmoneyReportService


def test_extract_initdata_success():
    html = """
    <script>
      var initdata = {"hits":2,"size":50,"data":[
        {"title":"测试研报","stockName":"测试股份","stockCode":"000001","orgSName":"测试机构","publishDate":"2026-01-20 00:00:00.000","infoCode":"AP202601200001"},
        {"title":"第二条","stockName":"测试股份","stockCode":"000002","orgSName":"测试机构","publishDate":"2026-01-19 00:00:00.000","infoCode":"AP202601200002"}
      ]};
    </script>
    """
    service = EastmoneyReportService()
    data = service._extract_initdata(html)
    assert data is not None
    assert data["hits"] == 2
    assert len(data["data"]) == 2


def test_extract_initdata_failure():
    html = "<html><body>no initdata</body></html>"
    service = EastmoneyReportService()
    data = service._extract_initdata(html)
    assert data is None


def test_extract_zwinfo_success():
    html = """
    <script>
      var zwinfo = {"notice_content":"测试正文\r\n第二行","info_code":"AP202601200003","publish_date":"2026-01-20 00:00:00","org_name":"测试机构","rating":"买入","attach_url":"https://pdf.example.com/1.pdf"};
    </script>
    """
    service = EastmoneyReportService()
    data = service._extract_zwinfo(html)
    assert data is not None
    assert data["notice_content"].startswith("测试正文")


def test_normalize_item_maps_fields():
    raw = {
        "title": "测试研报",
        "stockName": "测试股份",
        "stockCode": "000001",
        "orgSName": "测试机构",
        "publishDate": "2026-01-20 00:00:00.000",
        "infoCode": "AP202601200001",
        "emRatingName": "买入",
        "indvInduName": "通信设备",
    }
    service = EastmoneyReportService()
    item = service._normalize_item(raw, "stock")
    assert item["id"] == "AP202601200001"
    assert item["title"] == "测试研报"
    assert item["stock_name"] == "测试股份"
    assert item["stock_code"] == "000001"
    assert item["org_name"] == "测试机构"
    assert item["rating"] == "买入"
    assert item["industry"] == "通信设备"
    assert item["category"] == "stock"
    assert item["source"] == "eastmoney"
