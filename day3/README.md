# Day 3：LangGraph 多步骤 Agent

负责人：待团队认领。当前仅保留规划，下面的业务子目录由负责人开发时创建。

| 建议目录 | 课程任务 | 实现范围 |
| --- | --- | --- |
| `demo01_diagnosis/` | 自动排查与诊断 Agent | 定义状态、规划步骤、查询历史数据、对比标准参数、输出诊断建议；包含终止条件和工具失败处理。 |

## 开发要求

- Agent / 工作流编排统一使用 LangGraph，复用 `common/` 的配置、模型、状态和工具节点。
- 目录结构按 [根 README](../README.md)，代码约定见 [开发说明](../docs/development.md)。
- 模型、数据读取库、向量库等新增依赖在根目录统一锁定，参见 [版本信息](../docs/versions.md)。
- 每个业务目录完成后补齐自己的 README、样例数据和必要的业务测试。

原始课程中的 Semantic Kernel、AutoGen / CrewAI 保留为框架介绍内容；实际代码全部围绕 LangGraph 编写，不建立其他框架的实现目录。
