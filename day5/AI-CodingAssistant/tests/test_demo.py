import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


DEMO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO_DIR))

from common.config import AppSettings, LLMProvider, RunMode  # noqa: E402
from common.graph import build_run_config, new_thread_id  # noqa: E402
from demo import ModelClient, SAMPLE_REQUIREMENT, build_graph  # noqa: E402
from mock_data import BUGGY_CODE  # noqa: E402


class CodingAssistantTests(unittest.TestCase):
    def setUp(self):
        self.model = ModelClient(AppSettings(_env_file=None, run_mode=RunMode.MOCK))

    def test_generate_review_and_tests(self):
        result = build_graph(self.model).invoke(
            {"action": "generate", "user_query": SAMPLE_REQUIREMENT, "model_calls": 0},
            build_run_config(thread_id=new_thread_id()),
        )
        self.assertIn("summarize_counts", result["code"])
        self.assertEqual(result["findings"], [])
        self.assertIn("unittest", result["unit_tests"])
        self.assertIn("unittest", result["api_tests"])

    def test_review_detects_unweighted_average(self):
        code = (DEMO_DIR / "examples" / "buggy_code.py").read_text(encoding="utf-8")
        self.assertEqual(code, BUGGY_CODE)
        result = build_graph(self.model).invoke(
            {"action": "review", "code": code, "model_calls": 0},
            build_run_config(thread_id=new_thread_id()),
        )
        self.assertEqual([item["category"] for item in result["findings"]], ["logic"])
        self.assertIn("简单平均", result["findings"][0]["message"])

    def test_mock_rejects_arbitrary_review(self):
        with self.assertRaisesRegex(ValueError, "真实模型"):
            build_graph(self.model).invoke(
                {"action": "review", "code": "x = 1\n", "model_calls": 0},
                build_run_config(thread_id=new_thread_id()),
            )

    def test_real_review_calls_model(self):
        settings = AppSettings(
            _env_file=None,
            run_mode=RunMode.REAL,
            llm_provider=LLMProvider.OPENAI_COMPATIBLE,
            llm_model="demo-model",
            llm_base_url="https://example.test/v1",
        )
        finding = {"category": "logic", "severity": "high", "line": 8,
                   "message": "比率计算错误", "suggestion": "先汇总后相除"}
        response = Mock()
        response.json.return_value = {"choices": [{"message": {
            "content": json.dumps({"findings": [finding]}, ensure_ascii=False)
        }}]}
        with patch("demo.httpx.post", return_value=response) as post:
            result = build_graph(ModelClient(settings)).invoke(
                {"action": "review", "code": BUGGY_CODE, "model_calls": 0},
                build_run_config(thread_id=new_thread_id()),
            )
        self.assertEqual(result["findings"], [finding])
        self.assertEqual(result["model_calls"], 1)
        self.assertIn("待审查代码", post.call_args.kwargs["json"]["messages"][1]["content"])

    def test_real_model_request_uses_configured_endpoint(self):
        settings = AppSettings(
            _env_file=None,
            run_mode=RunMode.REAL,
            llm_provider=LLMProvider.OPENAI_COMPATIBLE,
            llm_model="demo-model",
            llm_base_url="https://example.test/v1",
        )
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": '{"code": "x = 1"}'}}]}
        with patch("demo.httpx.post", return_value=response) as post:
            result = ModelClient(settings).ask("generate", "演示需求")
        self.assertEqual(result, {"code": "x = 1"})
        self.assertEqual(post.call_args.args[0], "https://example.test/v1/chat/completions")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "demo-model")


if __name__ == "__main__":
    unittest.main()
