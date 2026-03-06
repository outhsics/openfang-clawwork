#!/usr/bin/env python3
"""Export OpenFang-friendly bridge assets from ClawWork task value metadata."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


AGENT_RULES = [
    ("legal-assistant", ["lawyer", "legal", "contract", "agreement", "compliance", "regulatory", "audit test", "bankruptcy", "case creation", "risk assessment"]),
    ("analyst", ["excel", "workbook", "spreadsheet", "model", "npv", "reconcile", "financial", "trial balance", "forecast", "variance", "calculate", "p&l"]),
    ("researcher", ["research", "publicly available", "academic articles", "compare", "evaluate", "locate", "sources", "citations", "study", "summary"]),
    ("sales-assistant", ["supplier", "procurement", "sourcing", "nomination", "proposal", "negotiation", "crm", "pipeline", "outreach", "client-ready"]),
    ("customer-support", ["customer", "service representative", "support", "intake", "case notes", "tracking"]),
    ("writer", ["memo", "briefing note", "procedure", "policy", "report", "one-page", "document", "word", "pdf", "deck", "presentation"]),
]

HIGH_FIT_KEYWORDS = [
    "excel", "word", "pdf", "report", "memo", "proposal", "briefing note",
    "checklist", "procedure", "analysis", "recommendation", "compare",
    "research", "summary", "table", "workbook", "draft",
]

LOW_FIT_KEYWORDS = [
    "wav", "mp3", "stems", "mix", "instrumental", "thumbnail", "voice-over",
    "stage plot", "vertical shorts", "captions", "drum reference", "sax",
    "bass performance", "video", "audio", "touring band",
]

MULTI_ARTIFACT_KEYWORDS = [
    "plus", "three-part", "package", "and produce", "and deliver", "along with",
    "export and submit", "zip", "png", "xlsx", "docx", "pptx", "pdf",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export OpenFang bridge assets from ClawWork task values.")
    parser.add_argument("--input", required=True, help="Path to task_values.jsonl")
    parser.add_argument("--output", required=True, help="Output repo root")
    return parser.parse_args()


def load_tasks(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pick_agent(task: dict) -> str:
    text = f"{task['occupation']} {task['task_summary']}".lower()
    for agent, keywords in AGENT_RULES:
        if any(keyword in text for keyword in keywords):
            return agent
    occupation = task["occupation"].lower()
    if "manager" in occupation or "supervisor" in occupation:
        return "writer"
    if "engineer" in occupation or "systems" in occupation:
        return "analyst"
    return "researcher"


def deliverable_flags(summary: str) -> dict[str, bool]:
    text = summary.lower()
    return {
        "spreadsheet": any(word in text for word in ["excel", "workbook", "spreadsheet", "model"]),
        "doc": any(word in text for word in ["word", "memo", "procedure", "policy", "briefing", "report", "proposal"]),
        "pdf": "pdf" in text,
        "slides": any(word in text for word in ["powerpoint", "deck", "presentation"]),
        "research": any(word in text for word in ["research", "articles", "publicly available", "sources"]),
        "creative_media": any(word in text for word in LOW_FIT_KEYWORDS),
    }


def macro_group(task: dict) -> str:
    summary = task["task_summary"].lower()
    occ = task["occupation"].lower()
    flags = deliverable_flags(summary)

    if flags["creative_media"]:
        return "Creative Media Production"
    if any(word in summary for word in ["compliance", "regulatory", "audit", "form 1040", "legal", "bankruptcy", "case creation"]) or "lawyer" in occ:
        return "Legal, Compliance and Case Documentation"
    if any(word in summary for word in ["supplier", "sourcing", "procurement", "nomination", "cpo", "sales", "crm", "pipeline"]) or "purchasing" in occ:
        return "Procurement, Sales and Vendor Strategy"
    if flags["spreadsheet"] or any(word in summary for word in ["financial", "npv", "trial balance", "p&l", "forecast", "variance", "amortizes"]):
        return "Spreadsheet and Financial Operations"
    if flags["research"] or any(word in summary for word in ["policy", "briefing note", "articles", "evidence", "evaluation plan"]):
        return "Research, Policy and Briefing"
    if any(word in summary for word in ["customer", "case notes", "tracking", "checklist", "form", "schedule", "intake", "guide"]):
        return "Administrative, Customer and Form Work"
    if flags["slides"] or any(word in summary for word in ["training", "session", "curriculum", "presentation"]):
        return "Decks, Training and Communications"
    return "Technical and General Business Planning"


def fit_score(task: dict) -> int:
    summary = task["task_summary"].lower()
    occupation = task["occupation"].lower()
    value = float(task["task_value_usd"])
    flags = deliverable_flags(summary)

    score = 45
    score += min(18, int((value - 120) / 8))

    if flags["spreadsheet"]:
        score += 14
    if flags["doc"]:
        score += 12
    if flags["pdf"]:
        score += 4
    if flags["slides"]:
        score += 2
    if flags["research"]:
        score += 10
    if any(keyword in summary for keyword in HIGH_FIT_KEYWORDS):
        score += 8
    if any(keyword in occupation for keyword in ["accountant", "financial", "compliance", "administrative", "purchasing", "sales", "editor", "analyst", "lawyer"]):
        score += 8
    if any(keyword in occupation for keyword in ["nurse", "pharmacist", "social worker"]):
        score -= 8
    if "form 1040" in summary:
        score -= 10
    if flags["creative_media"]:
        score -= 35

    artifact_hits = sum(keyword in summary for keyword in MULTI_ARTIFACT_KEYWORDS)
    if artifact_hits >= 4:
        score -= 12
    elif artifact_hits >= 2:
        score -= 6

    if any(word in summary for word in ["bilingual", "ocr", "image", "diagram", "public-domain images"]):
        score -= 6

    return max(0, min(100, score))


def commercial_score(task: dict) -> float:
    fit = fit_score(task)
    value = float(task["task_value_usd"])
    normalized_value = min(100.0, value / 2.8)
    return round(fit * 0.75 + normalized_value * 0.25, 2)


def fit_band(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 65:
        return "medium-high"
    if score >= 50:
        return "medium"
    return "low"


def reason(task: dict) -> str:
    flags = deliverable_flags(task["task_summary"].lower())
    reasons: list[str] = []
    if flags["spreadsheet"]:
        reasons.append("clear spreadsheet-style output")
    if flags["doc"]:
        reasons.append("document-heavy deliverable")
    if flags["research"]:
        reasons.append("research-first workflow")
    if flags["creative_media"]:
        reasons.append("specialized media tooling required")
    if not reasons:
        reasons.append("general business artifact")
    return ", ".join(reasons)


def build_record(task: dict) -> dict:
    score = fit_score(task)
    return {
        "task_id": task["task_id"],
        "occupation": task["occupation"],
        "sector": task["sector"],
        "task_value_usd": round(float(task["task_value_usd"]), 2),
        "hours_estimate": task["hours_estimate"],
        "task_summary": task["task_summary"],
        "openfang_agent": pick_agent(task),
        "macro_group": macro_group(task),
        "fit_score": score,
        "fit_band": fit_band(score),
        "commercial_score": commercial_score(task),
        "bridge_mode": "summary-only",
        "fit_reason": reason(task),
        "execution_note": "Full runnable prompt/reference files still require the GDPVal parquet source.",
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def grouped_summary(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["macro_group"]].append(row)

    summary = []
    for group, items in grouped.items():
        summary.append(
            {
                "group": group,
                "count": len(items),
                "avg_fit": round(sum(item["fit_score"] for item in items) / len(items), 1),
                "avg_value": round(sum(item["task_value_usd"] for item in items) / len(items), 2),
                "most_common_agents": Counter(item["openfang_agent"] for item in items).most_common(3),
                "top_occupations": Counter(item["occupation"] for item in items).most_common(3),
            }
        )
    summary.sort(key=lambda row: (row["avg_fit"], row["avg_value"]), reverse=True)
    return summary


def workflow_definition() -> dict:
    return {
        "name": "clawwork-doc-task-pipeline",
        "description": "Run a ClawWork document-style task stub through OpenFang researcher -> analyst -> writer.",
        "steps": [
            {
                "name": "scope-task",
                "agent_name": "researcher",
                "prompt": "Break this task into assumptions, missing inputs, and recommended sources. Task: {{input}}",
                "mode": "sequential",
                "timeout_secs": 120,
                "error_mode": "fail",
                "output_var": "scope",
            },
            {
                "name": "draft-artifact",
                "agent_name": "analyst",
                "prompt": "Create the first-pass business artifact for this task. Use the scope notes first, then the task. Scope: {{scope}}. Task: {{input}}",
                "mode": "sequential",
                "timeout_secs": 180,
                "error_mode": "fail",
                "output_var": "draft",
            },
            {
                "name": "polish-delivery",
                "agent_name": "writer",
                "prompt": "Turn this draft into a client-ready deliverable summary with clear sections, assumptions, and next required files. Draft: {{draft}}",
                "mode": "sequential",
                "timeout_secs": 120,
                "error_mode": "fail",
            },
        ],
    }


def markdown_report(summary_rows: list[dict], top30: list[dict], pilot: list[dict]) -> str:
    lines = [
        "# ClawWork to OpenFang Fit Report",
        "",
        "This report is generated from `task_values.jsonl` metadata only.",
        "",
        "Constraint:",
        "- current exports are `summary-only` task stubs",
        "- full execution needs the GDPVal parquet task source",
        "",
        "## Grouped fit",
        "",
        "| Group | Tasks | Avg fit | Avg value | Common agents |",
        "| --- | ---: | ---: | ---: | --- |",
    ]

    for row in summary_rows:
        common_agents = ", ".join(f"{name} x{count}" for name, count in row["most_common_agents"])
        lines.append(f"| {row['group']} | {row['count']} | {row['avg_fit']} | ${row['avg_value']} | {common_agents} |")

    lines.extend(
        [
            "",
            "## Top 30 real service directions",
            "",
            "| # | Occupation | Value | Agent | Fit | Direction |",
            "| --- | --- | ---: | --- | ---: | --- |",
        ]
    )

    for idx, row in enumerate(top30, start=1):
        lines.append(
            f"| {idx} | {row['occupation']} | ${row['task_value_usd']} | {row['openfang_agent']} | {row['fit_score']} | {row['task_summary']} |"
        )

    lines.extend(
        [
            "",
            "## Pilot 3 tasks",
            "",
            "| Task ID | Occupation | Value | Agent | Why it is a good first run |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )

    for row in pilot:
        lines.append(
            f"| {row['task_id']} | {row['occupation']} | ${row['task_value_usd']} | {row['openfang_agent']} | {row['fit_reason']} |"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_root = Path(args.output).expanduser().resolve()

    data_dir = output_root / "data"
    workflows_dir = output_root / "workflows"
    reports_dir = output_root / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks(input_path)
    rows = [build_record(task) for task in tasks]
    rows.sort(key=lambda row: (row["commercial_score"], row["fit_score"], row["task_value_usd"]), reverse=True)

    top60 = rows[:60]
    pilot = [row for row in rows if row["fit_score"] >= 78 and row["openfang_agent"] in {"analyst", "researcher", "writer", "legal-assistant", "sales-assistant"}][:3]
    top30 = [row for row in rows if row["fit_score"] >= 70][:30]
    summary_rows = grouped_summary(rows)

    write_jsonl(data_dir / "openfang_task_batch_top60.jsonl", top60)
    write_jsonl(data_dir / "openfang_pilot_3.jsonl", pilot)
    write_jsonl(data_dir / "top30_service_directions.jsonl", top30)

    with (data_dir / "grouped_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_rows, handle, indent=2)
        handle.write("\n")

    with (workflows_dir / "clawwork_doc_task_pipeline.json").open("w", encoding="utf-8") as handle:
        json.dump(workflow_definition(), handle, indent=2)
        handle.write("\n")

    with (reports_dir / "clawwork_openfang_fit_report.md").open("w", encoding="utf-8") as handle:
        handle.write(markdown_report(summary_rows, top30, pilot))

    print(f"Generated bridge assets under {output_root}")


if __name__ == "__main__":
    main()
