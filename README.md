# LangGraph Agent 课程开发基础

这是五天 Agent 开发课程的协作仓库。 各天负责人在此基础上补充自己的课程代码。

# 安装依赖

本项目统一使用 [uv](https://docs.astral.sh/uv/) 管理依赖，不需要手动创建虚拟环境或安装 Python。

## 前置要求

只需要安装 uv（官方安装方式，任选其一）：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS（Homebrew）
brew install uv
```

```powershell
# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 安装步骤

**所有命令都在项目根目录执行**。

```bash
uv sync

cp .env.example .env
```

> `.env` 已在 `.gitignore` 中，不会被提交；`uv sync` 只负责虚拟环境，不会自动生成 `.env`。


## 运行代码

用 `uv run` 执行脚本

```bash
uv run python dayX/xxx.py
```

## 可自选功能依赖

某一天的 Demo 需要额外依赖时，用 `uv add` 安装：

```bash
uv add <包名>
```

`uv add` 会同时更新 `pyproject.toml` 和 `uv.lock`，**这两个文件都要提交**，否则其他同学执行 `uv sync` 拿不到同样的版本。

新增依赖后，请在对应的 `dayN/README.md` 中注明包名和用途，方便其他人了解。

