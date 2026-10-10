# 代码辅助助手

这个演示只有一条主要流程：**需求 → 生成 Python 代码 → 审查 → 生成单元测试和 API 测试**。也可以只审查已有 Python 文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `demo.py` | 三个图节点、模型调用、命令行入口 |
| `scanner.py` | Python AST 规则检查 |
| `mock_data.py` | 固定的不良率演示代码及测试 |
| `examples/buggy_code.py` | 故意留有问题的审查样例 |
| `tests/test_demo.py` | 核心流程测试 |

## 运行

在**仓库根目录**执行：

```bash
PYTHONPATH=. uv run python "day5/AI-Coding Assistant/demo.py"
```

- `solution.py`：生成的业务代码和 WSGI API
- `review.json`：审查意见
- `test_solution.py`：单元测试
- `test_api.py`：API 测试（直接调用 WSGI 应用，无需启动服务器）

运行生成的测试：

```bash
uv run python -m unittest discover -s "day5/AI-Coding Assistant/outputs/runtime" -p "test_*.py" -v
```

审查有缺陷的代码：

```bash
PYTHONPATH=. uv run python "day5/AI-Coding Assistant/demo.py" --review "day5/AI-Coding Assistant/examples/buggy_code.py"
```

也可以用 `--requirement "你的需求"` 输入其他任务；这需要真实模型。设置 `.env` 中的 `RUN_MODE=real`、`LLM_PROVIDER=openai`（或 `openai_compatible`）、`LLM_MODEL`、`LLM_API_KEY`，兼容接口还需 `LLM_BASE_URL`。真实模式调用兼容 Chat Completions 的接口；模拟模式只演示固定的不良率需求，并会明确拒绝其他生成需求。

## 流程和边界

```text
生成：START → generate → review → generate_tests → END
审查：START → review → END
```

静态扫描会指出审查样例中“逐行计算不良率后求简单平均”的口径错误和空数据除零风险，也保留直接拼接 SQL、未用 `with` 关闭文件、向全局列表无限追加等**潜在**问题检查。真实模型会补充代码审查意见；这些检查不能证明代码没有其他漏洞。生成的代码和测试只写入输出目录，不会自动执行。
