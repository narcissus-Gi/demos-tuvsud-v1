---
name: production-anomaly-analyzer
description: 分析生产统计数据中的异常。当用户要求“分析生产异常”“检查夜班数据”“生产异常报告”时使用。不用于日常简单的数据查询。
---

# 生产异常分析流程

## 硬规则
- 所有数字必须来自 Excel 文件查询结果，禁止编造或猜测。
- 异常判断必须依据 references/rules.md 中的定义。

## 执行步骤

### 第 1 步：查询数据
通过读取 assets/data/errors.xlsx 文件，获取生产异常数据。

### 第 2 步：数据校验
读取 references/rules.md，按其中定义的阈值和判断逻辑逐项检查。

### 第 3 步：给出结论
读取 assets/data/history.xlsx 文件，该文件包括了以往的生产异常案例以及解决办法。读取该文件寻找当前异常事件可能的异常原因以及解决方法。

### 第 4 步：生成报告
按 assets/report_template.md 格式输出 Markdown。