"""工厂产线不良率需求的固定离线演示数据。"""

SAMPLE_REQUIREMENT = (
    "统计多条产线记录的不良率：每条记录包含 total_count 和 defect_count。"
    "先汇总数量，再用总不良品数除以总产量，返回 0 到 1 的比率；"
    "总产量为 0 时返回空比率和 no_data 状态。提供接收 JSON 数据的 API。"
)

BUGGY_CODE = '''"""用于演示代码审查的故意含错代码，不要用于生产环境。"""

history = []

def bad_rate(rows):
    rates = [r["defect_count"] / r["total_count"]
             for r in rows]
    return sum(rates) / len(rates)
'''

BUGGY_REVIEW = [{
    "category": "logic",
    "severity": "high",
    "line": 8,
    "message": "逐行不良率的简单平均值可能偏离整体不良率；空记录或某行零产量还会导致除零。",
    "suggestion": "先分别汇总不良品数和总产量，再相除；总产量为 0 时返回无数据。",
}]

SAMPLE_CODE = '''"""计算工厂产线不良率"""

import json


def summarize_counts(rows):
    total = defects = 0
    for row in rows:
        t = row["total_count"]
        d = row["defect_count"]
        if type(t) is not int or type(d) is not int:
            raise ValueError("产量和不良品数量必须是整数")
        if t < 0 or d < 0 or d > t:
            raise ValueError("产量或不良品数量不合法")
        total += t
        defects += d
    return {
        "total_count": total,
        "defect_count": defects,
        "defect_rate": defects / total if total else None,
        "status": "ok" if total else "no_data",
    }


def app(environ, start_response):
    """通过 POST /defect-rate 汇总多条产线记录，返回 JSON。"""
    if environ.get("PATH_INFO") != "/defect-rate":
        status, payload = "404 Not Found", {"error": "接口不存在"}
    elif environ.get("REQUEST_METHOD") != "POST":
        status, payload = "405 Method Not Allowed", {"error": "请使用 POST 请求"}
    else:
        try:
            length = int(environ.get("CONTENT_LENGTH", "0"))
            request = json.loads(environ["wsgi.input"].read(length))
            rows = request["rows"]
            if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
                raise ValueError("rows 必须是记录列表")
            status = "200 OK"
            payload = summarize_counts(rows)
        except (KeyError, TypeError, ValueError) as error:
            status, payload = "400 Bad Request", {"error": str(error)}
    body = json.dumps(payload).encode("utf-8")
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]
'''

UNIT_TESTS = '''import unittest

from solution import summarize_counts


class DefectRateTests(unittest.TestCase):
    def test_multiple_rows_use_total_counts(self):
        rows = [
            {"total_count": 100, "defect_count": 10},
            {"total_count": 900, "defect_count": 0},
        ]
        self.assertEqual(summarize_counts(rows), {
            "total_count": 1000,
            "defect_count": 10,
            "defect_rate": 0.01,
            "status": "ok",
        })

    def test_empty_rows_have_no_data(self):
        self.assertEqual(summarize_counts([]), {
            "total_count": 0,
            "defect_count": 0,
            "defect_rate": None,
            "status": "no_data",
        })

    def test_zero_total_has_no_data(self):
        result = summarize_counts([{"total_count": 0, "defect_count": 0}])
        self.assertIsNone(result["defect_rate"])
        self.assertEqual(result["status"], "no_data")

    def test_invalid_counts(self):
        rows = [
            {"total_count": 10, "defect_count": -1},
            {"total_count": 10, "defect_count": 11},
            {"total_count": "10", "defect_count": 1},
            {"total_count": True, "defect_count": 1},
        ]
        for row in rows:
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    summarize_counts([row])


if __name__ == "__main__":
    unittest.main()
'''

API_TESTS = '''import json
import unittest
from io import BytesIO

from solution import app


def request(path, payload=None, method="POST"):
    response = {}

    def start_response(status, headers):
        response["status"] = status
        response["headers"] = headers

    data = json.dumps(payload or {}).encode("utf-8")
    environ = {
        "PATH_INFO": path,
        "REQUEST_METHOD": method,
        "CONTENT_LENGTH": str(len(data)),
        "wsgi.input": BytesIO(data),
    }
    body = b"".join(app(environ, start_response))
    return response["status"], json.loads(body)


class DefectRateApiTests(unittest.TestCase):
    def test_success(self):
        status, body = request("/defect-rate", {"rows": [
            {"total_count": 100, "defect_count": 10},
            {"total_count": 900, "defect_count": 0},
        ]})
        self.assertEqual(status, "200 OK")
        self.assertEqual(body["defect_rate"], 0.01)
        self.assertEqual(body["total_count"], 1000)

    def test_empty_rows(self):
        status, body = request("/defect-rate", {"rows": []})
        self.assertEqual(status, "200 OK")
        self.assertIsNone(body["defect_rate"])
        self.assertEqual(body["status"], "no_data")

    def test_bad_input(self):
        status, body = request("/defect-rate", {"rows": [
            {"total_count": 10, "defect_count": 11},
        ]})
        self.assertEqual(status, "400 Bad Request")
        self.assertIn("error", body)

    def test_wrong_method(self):
        status, _ = request("/defect-rate", method="GET")
        self.assertEqual(status, "405 Method Not Allowed")

    def test_unknown_path(self):
        status, _ = request("/unknown")
        self.assertEqual(status, "404 Not Found")


if __name__ == "__main__":
    unittest.main()
'''
