#!/usr/bin/env python3
"""Backfill an OpenFang run into a ClawWork-style agent_data directory."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill an OpenFang result into ClawWork-style logs.")
    parser.add_argument("--agent-data-root", required=True, help="Root folder for ClawWork-style agent data.")
    parser.add_argument("--signature", required=True, help="Agent signature.")
    parser.add_argument("--task-id", required=True, help="Task identifier.")
    parser.add_argument("--date", required=True, help="Task date in YYYY-MM-DD.")
    parser.add_argument("--occupation", required=True, help="Task occupation.")
    parser.add_argument("--sector", required=True, help="Task sector.")
    parser.add_argument("--prompt", required=True, help="Task prompt or task summary.")
    parser.add_argument("--payment", type=float, required=True, help="Task payment in USD.")
    parser.add_argument("--evaluation-score", type=float, required=True, help="Evaluation score.")
    parser.add_argument("--feedback", default="", help="Evaluation feedback.")
    parser.add_argument("--token-cost", type=float, required=True, help="Token or execution cost in USD.")
    parser.add_argument("--wall-clock-seconds", type=int, required=True, help="Elapsed wall clock time.")
    parser.add_argument("--reasoning", default="Executed through OpenFang workflow.", help="Decision reasoning.")
    parser.add_argument("--memory-topic", default="", help="Optional memory topic.")
    parser.add_argument("--memory-content", default="", help="Optional memory content.")
    parser.add_argument("--artifact", action="append", default=[], help="Path to an output artifact to copy into sandbox/<date>/ .")
    parser.add_argument("--terminal-log", default="", help="Optional path to a terminal log text file.")
    parser.add_argument("--initial-balance", type=float, default=1000.0, help="Initial balance if the agent folder is new.")
    return parser.parse_args()


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def read_last_jsonl(path: Path) -> dict | None:
    if not path.exists():
        return None
    last = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = json.loads(line)
    return last


def ensure_initial_balance(balance_file: Path, initial_balance: float) -> dict:
    latest = read_last_jsonl(balance_file)
    if latest is not None:
        return latest
    record = {
        "date": "initialization",
        "balance": initial_balance,
        "net_worth": initial_balance,
        "survival_status": "stable",
        "total_token_cost": 0.0,
        "total_work_income": 0.0,
    }
    append_jsonl(balance_file, record)
    return record


def survival_status(balance: float) -> str:
    if balance <= 0:
        return "bankrupt"
    if balance <= 100:
        return "struggling"
    if balance <= 500:
        return "stable"
    return "thriving"


def write_terminal_log(path: Path, task_id: str, score: float, payment: float, feedback: str) -> None:
    lines = [
        f"[09:00] Loaded {task_id}",
        "[09:05] OpenFang workflow started",
        "[09:45] Draft artifact completed",
        f"[09:57] Evaluation completed with score {score:.2f}",
        f"[09:58] Payment received: ${payment:.2f}",
    ]
    if feedback:
        lines.append(f"[09:59] Feedback: {feedback}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_artifacts(artifact_paths: list[str], sandbox_dir: Path) -> list[str]:
    copied: list[str] = []
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    for raw_path in artifact_paths:
        src = Path(raw_path).expanduser().resolve()
        if not src.exists() or not src.is_file():
            continue
        dest = sandbox_dir / src.name
        shutil.copy2(src, dest)
        copied.append(str(dest))
    return copied


def main() -> None:
    args = parse_args()
    root = Path(args.agent_data_root).expanduser().resolve()
    agent_dir = root / args.signature

    decisions_file = agent_dir / "decisions" / "decisions.jsonl"
    balance_file = agent_dir / "economic" / "balance.jsonl"
    completions_file = agent_dir / "economic" / "task_completions.jsonl"
    tasks_file = agent_dir / "work" / "tasks.jsonl"
    evaluations_file = agent_dir / "work" / "evaluations.jsonl"
    memory_file = agent_dir / "memory" / "memory.jsonl"
    sandbox_dir = agent_dir / "sandbox" / args.date
    terminal_log_file = agent_dir / "terminal_logs" / f"{args.date}.log"

    previous = ensure_initial_balance(balance_file, args.initial_balance)
    prev_balance = float(previous["balance"])
    prev_total_token_cost = float(previous.get("total_token_cost", 0.0))
    prev_total_work_income = float(previous.get("total_work_income", 0.0))

    new_total_token_cost = prev_total_token_cost + args.token_cost
    new_total_work_income = prev_total_work_income + args.payment
    new_balance = prev_balance - args.token_cost + args.payment

    append_jsonl(
        tasks_file,
        {
            "task_id": args.task_id,
            "date": args.date,
            "sector": args.sector,
            "occupation": args.occupation,
            "prompt": args.prompt,
        },
    )

    append_jsonl(
        evaluations_file,
        {
            "task_id": args.task_id,
            "payment": args.payment,
            "feedback": args.feedback,
            "evaluation_score": args.evaluation_score,
            "evaluation_method": "openfang-manual-backfill",
        },
    )

    append_jsonl(
        completions_file,
        {
            "task_id": args.task_id,
            "date": args.date,
            "timestamp": datetime.now().isoformat(),
            "wall_clock_seconds": args.wall_clock_seconds,
            "work_submitted": True,
            "money_earned": args.payment,
            "evaluation_score": args.evaluation_score,
        },
    )

    append_jsonl(
        decisions_file,
        {
            "date": args.date,
            "activity": "work",
            "reasoning": args.reasoning,
        },
    )

    append_jsonl(
        balance_file,
        {
            "date": args.date,
            "task_id": args.task_id,
            "balance": round(new_balance, 4),
            "net_worth": round(new_balance, 4),
            "survival_status": survival_status(new_balance),
            "daily_token_cost": round(args.token_cost, 4),
            "work_income_delta": round(args.payment, 4),
            "total_token_cost": round(new_total_token_cost, 4),
            "total_work_income": round(new_total_work_income, 4),
        },
    )

    if args.memory_topic and args.memory_content:
        append_jsonl(
            memory_file,
            {
                "topic": args.memory_topic,
                "timestamp": datetime.now().isoformat(),
                "date": args.date,
                "knowledge": args.memory_content,
            },
        )

    copied_artifacts = copy_artifacts(args.artifact, sandbox_dir)

    if args.terminal_log:
        terminal_source = Path(args.terminal_log).expanduser().resolve()
        terminal_log_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(terminal_source, terminal_log_file)
    else:
        write_terminal_log(terminal_log_file, args.task_id, args.evaluation_score, args.payment, args.feedback)

    result = {
        "agent_dir": str(agent_dir),
        "task_id": args.task_id,
        "balance": round(new_balance, 4),
        "copied_artifacts": copied_artifacts,
        "terminal_log": str(terminal_log_file),
    }
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
