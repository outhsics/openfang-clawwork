[![CI](https://github.com/outhsics/openfang-clawwork/actions/workflows/ci.yml/badge.svg)](https://github.com/outhsics/openfang-clawwork/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# 💼 OpenFang ClawWork

<div align="center">

**面向真实办公室交付物的 OpenFang 商业开源任务桥接项目**

[![OpenFang](https://img.shields.io/badge/OpenFang-Agent%20OS-green.svg)](https://github.com/RightNow-AI/openfang)
[![Tasks](https://img.shields.io/badge/ClawWork-220%20tasks-orange.svg)](reports/clawwork_openfang_fit_report.md)
[![Bridge Mode](https://img.shields.io/badge/Bridge-summary--only-blue.svg)](data/openfang_task_batch_top60.jsonl)

[English](README_EN.md) | 简体中文

**把 ClawWork 的办公室任务筛选、分组、路由到 OpenFang，优先跑最像真实接单和赚钱的任务。**

[快速开始](#-快速开始) • [为什么值得做](#-为什么这个项目值得做) • [任务分组](#-最适合-openfang-赚钱的任务组) • [路线图](#-roadmap)

</div>

---

## Recruiter Snapshot

- Status: `active`
- Positioning: commercial-open-source bridge between ClawWork task inventory and OpenFang execution
- Core Value: find which office tasks are most worth automating before you waste tokens on weak categories
- Technical Scope: task ranking, batch export, workflow templates, OpenFang routing, execution backfill
- Delivery Signal: top-60 queue, top-3 pilot, top-30 service directions, reusable workflow payload
- Last Reviewed: `2026-03-06`

## 📖 About / 关于项目

### 🎯 项目简介

**OpenFang ClawWork** 是一个面向真实办公室工作的商业开源桥接项目。它不做泛泛的“AI 助手演示”，而是聚焦一个更值钱的问题：

> 在 ClawWork 的 220 个任务里，哪些任务真的适合交给 OpenFang 去跑，哪些最像你可以拿去做真实服务、交付文档、甚至验证 AI 赚钱能力的任务？

这个仓库把 `ClawWork` 的任务库存转成更适合 `OpenFang` 的资产包：

- 可优先试跑的任务 batch
- 更适合不同 agent 的任务路由
- 用于 OpenFang 的 workflow 定义
- 面向商业接单的任务方向筛选

### 🌟 为什么这个项目值得做

很多 agent 项目停留在：

- 聊天回答问题
- 做一个 demo 页面
- 跑几次 benchmark 就结束

但真正有商业价值的方向往往是：

- Excel 报表与财务模型
- 研究摘要与 briefing
- 采购/供应商/销售支持文档
- 合规与法务辅助文档
- 流程文档、memo、内部汇报材料

这些任务更接近：

- 企业内部降本增效
- 代理服务和交付
- 高客单价的信息处理工作
- 可被包装成真实 AI 服务产品

---

## 💰 这个项目能帮你找到什么样的“赚钱任务”

### ✅ 最有潜力的方向

基于当前评分，这几类最适合 OpenFang：

1. **Spreadsheet and Financial Operations**
   Excel 报表、财务包、预算模型、对账、预测。

2. **Research, Policy and Briefing**
   研究整理、政策摘要、管理层 briefing、来源归纳。

3. **Procurement, Sales and Vendor Strategy**
   采购方案、供应商对比、提案、流程优化、销售支持材料。

4. **Legal, Compliance and Case Documentation**
   合规检查、法规整理、法务辅助文档、案例文档。

### ❌ 暂时不适合优先做的方向

1. **Creative Media Production**
   音频 stem、混音、配乐、复杂视频资产，不适合当前这套桥接策略先跑。

2. **多产物强格式任务**
   例如同时要求 PPT + PDF + 图片 + 表格、并且格式标准极严的任务。

---

## 🧠 当前推荐的 OpenFang Agent 路由

- `analyst`
  适合 Excel、财务模型、运营分析、结构化数据交付。

- `researcher`
  适合资料检索、来源对比、研究总结、带证据链的输出。

- `writer`
  适合 memo、政策、流程文档、管理汇报、客户可读版本润色。

- `legal-assistant`
  适合法务、合规、合同、监管解释类任务。

- `sales-assistant`
  适合采购、供应商、proposal、商务支持材料。

---

## 📦 仓库里已经有什么

- [scripts/export_clawwork_openfang_assets.py](scripts/export_clawwork_openfang_assets.py)
  从 `task_values.jsonl` 生成所有桥接资产。

- [data/openfang_pilot_3.jsonl](data/openfang_pilot_3.jsonl)
  最适合先试跑的 3 个任务。

- [data/openfang_task_batch_top60.jsonl](data/openfang_task_batch_top60.jsonl)
  优先级最高的 60 个任务。

- [data/top30_service_directions.jsonl](data/top30_service_directions.jsonl)
  最像真实可接单服务的前 30 个方向。

- [data/grouped_summary.json](data/grouped_summary.json)
  按任务大类聚合后的评分摘要。

- [workflows/clawwork_doc_task_pipeline.json](workflows/clawwork_doc_task_pipeline.json)
  一个可直接注册到 OpenFang 的 workflow 模板。

- [reports/clawwork_openfang_fit_report.md](reports/clawwork_openfang_fit_report.md)
  面向人阅读的完整分析报告。

- [fixtures/sample_task_values.jsonl](fixtures/sample_task_values.jsonl)
  CI 和 smoke test 的小型 fixture。

- [tests/smoke_test.py](tests/smoke_test.py)
  导出脚本的最小测试。

---

## 🚀 快速开始

### 1. 启动 OpenFang

```bash
openfang start
```

### 2. 注册仓库自带 workflow

```bash
curl -X POST http://127.0.0.1:4200/api/workflows \
  -H 'Content-Type: application/json' \
  --data @workflows/clawwork_doc_task_pipeline.json
```

### 3. 从 pilot 包里挑一个任务试跑

参考 [data/openfang_pilot_3.jsonl](data/openfang_pilot_3.jsonl) 的 `task_summary`，直接作为 workflow 输入：

```bash
curl -X POST http://127.0.0.1:4200/api/workflows/<WORKFLOW_ID>/run \
  -H 'Content-Type: application/json' \
  -d '{"input":"Draft a professional memo explaining a rotating cleanup schedule and recreate the schedule into an editable Excel file."}'
```

### 4. 或者直接用 OpenAI-compatible API

```bash
curl -X POST http://127.0.0.1:4200/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openfang:analyst",
    "messages": [
      {"role": "user", "content": "Build a first-pass delivery plan for this task: Create a structured Excel P&L for a music tour using reference data and executive-ready formatting."}
    ]
  }'
```

---

## 🔬 当前限制

当前仓库是基于 ClawWork 暴露出来的任务价值元数据工作的，已知字段包括：

- `task_id`
- `occupation`
- `sector`
- `task_value_usd`
- `task_summary`
- `hours_estimate`

这足够做：

- 任务筛选
- 商业价值排序
- OpenFang agent 路由
- workflow 预编排

但还不够做：

- 全量可执行 prompt
- reference files 自动挂载
- 100% 原始任务重放

因为真正完整的任务输入仍然在 GDPVal parquet 数据源里。

所以当前导出资产的定位是：

**summary-only bridge assets**

---

## 🛠️ 开发

重新生成资产包：

```bash
python3 scripts/export_clawwork_openfang_assets.py \
  --input /path/to/task_values.jsonl \
  --output .
```

运行本地 smoke test：

```bash
python3 tests/smoke_test.py
```

---

## 🗺️ Roadmap

- 支持完整 GDPVal parquet 接入，让任务不再只是 summary-only
- 增加 task family 对应的 OpenFang workflow 模板
- 增加 OpenFang 执行结果回填到 ClawWork 风格日志的脚本
- 增加更细粒度的 agent routing profile
- 增加一个轻量 dashboard，用来浏览 220 个任务和 fit score

---

## 🤝 Contributing

看 [CONTRIBUTING.md](CONTRIBUTING.md)。这个仓库更欢迎“小而锋利”的改进，而不是无边界扩张。
