#!/usr/bin/env python3
"""Smoke test for the exporter."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_clawwork_openfang_assets.py"
FIXTURE = ROOT / "fixtures" / "sample_task_values.jsonl"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        out = Path(tmp_dir)
        subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(FIXTURE), "--output", str(out)],
            check=True,
        )

        required = [
            out / "data" / "openfang_pilot_3.jsonl",
            out / "data" / "openfang_task_batch_top60.jsonl",
            out / "data" / "top30_service_directions.jsonl",
            out / "data" / "grouped_summary.json",
            out / "workflows" / "clawwork_doc_task_pipeline.json",
            out / "reports" / "clawwork_openfang_fit_report.md",
        ]

        for path in required:
            assert_true(path.exists(), f"missing output: {path}")

        pilot_lines = (out / "data" / "openfang_pilot_3.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert_true(len(pilot_lines) >= 2, "expected at least two pilot tasks")

        first = json.loads(pilot_lines[0])
        assert_true("openfang_agent" in first, "pilot row missing openfang_agent")
        assert_true(first["fit_score"] >= 0, "invalid fit score")

        grouped = json.loads((out / "data" / "grouped_summary.json").read_text(encoding="utf-8"))
        assert_true(len(grouped) >= 2, "expected grouped summary rows")

        report = (out / "reports" / "clawwork_openfang_fit_report.md").read_text(encoding="utf-8")
        assert_true("Top 30 real service directions" in report, "report missing top 30 section")

    print("smoke test passed")


if __name__ == "__main__":
    main()
