# OpenFang ClawWork

Bridge project for running ClawWork-style office tasks through OpenFang without polluting an existing video-editing OpenFang repo.

## What this repo is for

- keep your video-editing OpenFang project separate from office-work task experiments
- pre-screen the 220 ClawWork tasks for OpenFang fit
- export task batches that are easy to route into OpenFang agents or workflows
- keep a reusable workflow example for document-heavy work

## Current scope

This repo works from ClawWork task value metadata:

- `task_id`
- `occupation`
- `sector`
- `task_value_usd`
- `task_summary`

That is enough to rank tasks, batch them, and pilot them in OpenFang.

Important limitation:

- full runnable prompts and reference files come from the GDPVal parquet dataset used by ClawWork
- this repo currently exports `summary-only` pilot assets unless you point it at the full dataset later

## Repo layout

- [scripts/export_clawwork_openfang_assets.py](scripts/export_clawwork_openfang_assets.py): build batches and reports from `task_values.jsonl`
- [data/openfang_pilot_3.jsonl](data/openfang_pilot_3.jsonl): first 3 tasks to try in OpenFang
- [data/openfang_task_batch_top60.jsonl](data/openfang_task_batch_top60.jsonl): top 60 screened tasks
- [data/top30_service_directions.jsonl](data/top30_service_directions.jsonl): most commercial task directions
- [data/grouped_summary.json](data/grouped_summary.json): grouped fit summary
- [workflows/clawwork_doc_task_pipeline.json](workflows/clawwork_doc_task_pipeline.json): OpenFang workflow example
- [reports/clawwork_openfang_fit_report.md](reports/clawwork_openfang_fit_report.md): human-readable analysis

## Best-fit task groups

The strongest categories for OpenFang are:

1. Spreadsheet and financial operations
2. Research, policy, and briefing
3. Procurement, sales, and vendor strategy
4. Legal, compliance, and case documentation

The weakest categories without extra tooling are:

1. Creative media production
2. Multi-artifact deck/media packages with strict format constraints

## Recommended OpenFang agents

- `analyst`: spreadsheets, financial models, operational analysis
- `researcher`: article gathering, source comparison, evidence-backed summaries
- `writer`: memos, procedures, briefings, client-ready rewrites
- `legal-assistant`: compliance, contract, case, and regulatory tasks
- `sales-assistant`: procurement, sourcing, supplier, outreach, and proposal work

## Quick start

1. Start OpenFang.

```bash
openfang start
```

2. Create the sample workflow.

```bash
curl -X POST http://127.0.0.1:4200/api/workflows \
  -H 'Content-Type: application/json' \
  --data @workflows/clawwork_doc_task_pipeline.json
```

3. Pick one item from [data/openfang_pilot_3.jsonl](data/openfang_pilot_3.jsonl) and use its `task_summary` as the workflow input.

```bash
curl -X POST http://127.0.0.1:4200/api/workflows/<WORKFLOW_ID>/run \
  -H 'Content-Type: application/json' \
  -d '{"input":"Draft a professional memo explaining a rotating cleanup schedule and recreate the schedule into an editable Excel file."}'
```

4. If you prefer direct agent calls, use the OpenAI-compatible endpoint:

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

## Regenerate assets

```bash
python3 scripts/export_clawwork_openfang_assets.py \
  --input /path/to/task_values.jsonl \
  --output .
```

## Why a separate repo

Your existing OpenFang project is video-editing specific. This repo isolates:

- different task prompts
- different workflows
- different output artifacts
- different success metrics

That separation is cleaner than mixing office-work experiments into a video-production tree.
