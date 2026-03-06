#!/usr/bin/env python3
"""Smoke test for ClawWork-style backfill output."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "backfill_openfang_result.py"
ARTIFACT = ROOT / "examples" / "cleanup-memo-case" / "delivery" / "cleanup_schedule.csv"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def last_jsonl(path: Path) -> dict:
    last = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = json.loads(line)
    assert_true(last is not None, f"expected records in {path}")
    return last


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir) / "agent_data"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--agent-data-root",
                str(root),
                "--signature",
                "openfang-pilot-agent",
                "--task-id",
                "pilot-001",
                "--date",
                "2026-03-06",
                "--occupation",
                "Administrative Services Managers",
                "--sector",
                "Government",
                "--prompt",
                "Draft a cleanup memo and editable schedule.",
                "--payment",
                "18.5",
                "--evaluation-score",
                "0.84",
                "--feedback",
                "Structured and practical.",
                "--token-cost",
                "2.75",
                "--wall-clock-seconds",
                "1800",
                "--artifact",
                str(ARTIFACT),
                "--memory-topic",
                "Ops delivery",
                "--memory-content",
                "Low ambiguity document plus schedule tasks are good pilot work.",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout.strip())
        agent_dir = Path(payload["agent_dir"])

        assert_true((agent_dir / "sandbox" / "2026-03-06" / "cleanup_schedule.csv").exists(), "artifact was not copied")
        assert_true((agent_dir / "terminal_logs" / "2026-03-06.log").exists(), "terminal log missing")
        assert_true(last_jsonl(agent_dir / "work" / "evaluations.jsonl")["evaluation_score"] == 0.84, "evaluation score mismatch")
        assert_true(last_jsonl(agent_dir / "economic" / "task_completions.jsonl")["money_earned"] == 18.5, "payment mismatch")
        assert_true(last_jsonl(agent_dir / "decisions" / "decisions.jsonl")["activity"] == "work", "decision activity mismatch")
        assert_true(last_jsonl(agent_dir / "memory" / "memory.jsonl")["topic"] == "Ops delivery", "memory topic mismatch")

    print("backfill smoke test passed")


if __name__ == "__main__":
    main()
