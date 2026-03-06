[![CI](https://github.com/outhsics/openfang-clawwork/actions/workflows/ci.yml/badge.svg)](https://github.com/outhsics/openfang-clawwork/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# OpenFang ClawWork

Commercial-open-source bridge for routing ClawWork office tasks into OpenFang agents and workflows.

This repo exists to answer a practical question:

> Which ClawWork tasks are actually worth running through OpenFang, and how do you batch them into something an agent stack can execute?

It keeps that work separate from any video-editing OpenFang project so the prompts, workflows, outputs, and success metrics do not get mixed together.

## What this repo gives you

- a screened view of all 220 ClawWork tasks
- a ranking of which task families are most likely to work with OpenFang
- a top-60 batch for queueing and a top-3 pilot for first execution
- a top-30 list of service directions that feel closest to real client work
- a reusable OpenFang workflow definition for document-heavy tasks
- a repeatable exporter script so the asset pack can be regenerated

## What it does not give you yet

This repo currently works from ClawWork task value metadata:

- `task_id`
- `occupation`
- `sector`
- `task_value_usd`
- `task_summary`
- `hours_estimate`

That is enough to rank and batch tasks, but not enough to run every task end-to-end.

Important limitation:

- the full runnable prompt plus reference files live in the GDPVal parquet source used by ClawWork
- current exports are therefore `summary-only` pilot assets

## Why this matters

Most agent demos die because they optimize for "can it answer" instead of "can it finish billable work."

This repo pushes toward the second question:

- spreadsheet work
- research briefs
- procurement and sourcing analysis
- compliance and legal documentation
- operational memos and internal reporting

Those are much closer to real office revenue than generic chatbot prompts.

## Best-fit task groups

Based on the current scoring pass, the strongest categories for OpenFang are:

1. Spreadsheet and financial operations
2. Research, policy, and briefing
3. Procurement, sales, and vendor strategy
4. Legal, compliance, and case documentation

Weakest without extra tooling:

1. Creative media production
2. Strict multi-artifact media/deck packages

## Recommended OpenFang agents

- `analyst`: spreadsheets, financial models, operations analysis
- `researcher`: evidence-backed research and synthesis
- `writer`: memos, procedures, briefings, client-ready rewrites
- `legal-assistant`: compliance, contracts, case, and regulatory work
- `sales-assistant`: sourcing, procurement, supplier strategy, proposals

## Repo layout

- [scripts/export_clawwork_openfang_assets.py](scripts/export_clawwork_openfang_assets.py)
  Builds all exported assets from `task_values.jsonl`.
- [data/openfang_pilot_3.jsonl](data/openfang_pilot_3.jsonl)
  The first three tasks to try in OpenFang.
- [data/openfang_task_batch_top60.jsonl](data/openfang_task_batch_top60.jsonl)
  Highest-priority screened batch.
- [data/top30_service_directions.jsonl](data/top30_service_directions.jsonl)
  Most commercial-looking task directions.
- [data/grouped_summary.json](data/grouped_summary.json)
  Fit summary by macro task group.
- [workflows/clawwork_doc_task_pipeline.json](workflows/clawwork_doc_task_pipeline.json)
  Example OpenFang workflow.
- [reports/clawwork_openfang_fit_report.md](reports/clawwork_openfang_fit_report.md)
  Human-readable report.
- [fixtures/sample_task_values.jsonl](fixtures/sample_task_values.jsonl)
  Tiny fixture for CI and smoke testing.
- [tests/smoke_test.py](tests/smoke_test.py)
  Minimal exporter smoke test.

## Quick start

1. Start OpenFang.

```bash
openfang start
```

2. Register the included workflow.

```bash
curl -X POST http://127.0.0.1:4200/api/workflows \
  -H 'Content-Type: application/json' \
  --data @workflows/clawwork_doc_task_pipeline.json
```

3. Pick a task from [data/openfang_pilot_3.jsonl](data/openfang_pilot_3.jsonl) and use its `task_summary` as workflow input.

```bash
curl -X POST http://127.0.0.1:4200/api/workflows/<WORKFLOW_ID>/run \
  -H 'Content-Type: application/json' \
  -d '{"input":"Draft a professional memo explaining a rotating cleanup schedule and recreate the schedule into an editable Excel file."}'
```

4. Or hit OpenFang through its OpenAI-compatible endpoint.

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

## Regenerate the asset pack

```bash
python3 scripts/export_clawwork_openfang_assets.py \
  --input /path/to/task_values.jsonl \
  --output .
```

## Development

Run the local smoke test:

```bash
python3 tests/smoke_test.py
```

## Roadmap

- support full GDPVal parquet ingestion so tasks are no longer summary-only
- emit OpenFang-ready workflow payloads per task family
- add task-to-agent routing profiles beyond the first heuristic pass
- add backfill scripts that write OpenFang execution results back into ClawWork-style logs
- add a small web report or dashboard for browsing the task inventory

## Contributing

Open [CONTRIBUTING.md](CONTRIBUTING.md) for the working rules. Small, sharp improvements are preferred over large speculative rewrites.
