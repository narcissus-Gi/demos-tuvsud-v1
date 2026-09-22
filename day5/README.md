# Day 5：AI 辅助开发与综合项目

负责人：待团队认领。当前仅保留规划，下面的业务子目录由负责人开发时创建。

| 建议目录 | 课程任务 | 实现范围 |
| --- | --- | --- |
| `demo01_coding_assistant/` | AI 辅助开发 | 围绕课程代码展示需求转代码、审查、Bug 修复和自动测试生成。 |
| `demo02_knowledge_agent/` | 知识库问答 Agent | 组合手册与 SOP 检索、多轮提问、纠错和排查步骤。 |
| `demo03_incident_agent/` | 生产异常分析 Agent | 结合日志、历史案例与 MES 状态输出有证据的分析报告。 |
| `demo04_mes_agent/` | MES 集成 Agent | 将自然语言转为只读查询和待确认工单，处理重复执行。 |
| `demo05_report_workflow/` | 报告生成工作流 | 组合数据库和文档提炼节点，输出注明来源的 Markdown 报告。 |

## 开发要求

- Agent / 工作流编排统一使用 LangGraph，复用 `common/` 的配置、模型、状态和工具节点。
- 目录结构按 [根 README](../README.md)，代码约定见 [开发说明](../docs/development.md)。
- 模型、数据读取库、向量库等新增依赖在根目录统一锁定，参见 [版本信息](../docs/versions.md)。
- 每个业务目录完成后补齐自己的 README、样例数据和必要的业务测试。
