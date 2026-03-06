# Contributing

## Scope

This repo is for the bridge between:

- ClawWork task inventory
- OpenFang execution paths
- commercial task selection and batching

Keep changes inside that boundary. Do not turn this repo into a generic OpenFang fork.

## Good contributions

- better task routing heuristics
- clearer workflow payloads
- tighter smoke tests
- cleaner asset exports
- better documentation for running tasks through OpenFang
- result backfill scripts once execution is wired up

## Avoid

- large refactors with no user-facing improvement
- adding heavy dependencies without a strong reason
- mixing unrelated video or media workflows into this repo

## Local check

```bash
python3 tests/smoke_test.py
python3 -m py_compile scripts/export_clawwork_openfang_assets.py
```
