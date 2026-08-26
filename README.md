# 修仙模拟器 · 问道长生 V0.1

这是一个本地可运行的基线项目。目标是先忠实保留《修仙模拟器 · 问道长生.docx》的规则与世界观，做出可启动、可创角、可推进回合、可修炼、可存读档的最小版本，再通过试玩逐步补全大模型叙事、数值引擎和网页界面。

## 当前实现

- Python 标准库即可运行，不依赖 Node、数据库或第三方包。
- 启动时直接读取 `docs/修仙模拟器 · 问道长生.docx`，原文是 V0.1 的权威规则源。
- 支持 `开始游戏`、默认/自定义创角备注、`面板`、`修炼`、自由行动、`存档`、`读档`、`帮助`。
- 一次普通输入只推进一个月；数值和历史写入 JSON 自动存档。
- `Narrator` 接口把叙事与游戏状态分开，后续可以接任意大模型 API，而不必改存档格式。

## 环境

- Windows 10/11
- Python 3.11 或更高版本（本机检测到 3.13.5）
- Node.js 暂不需要

## 首次启动

在 PowerShell 中执行：

```powershell
cd E:\Projects\xiuxian-simulator
.\.venv\Scripts\python.exe main.py
```

进入游戏后输入：

```text
开始游戏
确认默认创角
修炼
存档
```

退出可输入 `退出`、`quit` 或按 `Ctrl+C`。

## 运行测试

```powershell
cd E:\Projects\xiuxian-simulator
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 项目结构

```text
xiuxian-simulator/
├─ docs/                    原始规则文档（不改写）
├─ data/saves/              JSON 存档
├─ prompts/                 运行时补充约束
├─ src/xiuxian_simulator/   游戏状态、回合、存档和叙事接口
├─ tests/                   V0.1 烟雾测试
├─ main.py                  无需安装即可启动的入口
└─ pyproject.toml           Python 项目配置
```

## V0.1 边界

当前本地叙事器只负责让整条运行链先跑通，不宣称已经实现原文全部 21 章系统。宗门、情缘、完整战斗、技艺、NPC 世界演化与大模型生成仍是后续迭代。原始文档不会被程序改写；每次扩展应优先补测试，再修改规则引擎。

