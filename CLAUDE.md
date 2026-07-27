# CLAUDE.md

This file is intentionally minimal.

## Documentation Navigation

**Always start with [README.md](README.md)** — it is the master documentation index for this repository. It provides:
- Document categories by user intent (For Coders, Architecture & Design, Job State & Runtime, etc.)
- "When to Read" guidance for each document
- Document relationship diagrams
- Authority order for conflicting information

## Fact Resolution Order

Use this order when resolving facts:

1. The active workflow bundle under `workflows/<name>/`
2. The current runner code under `agent_runner_v2/`
3. Generated governance docs under `docs/system/00_governance/bootstrap/`
4. Root documentation (README.md, QWEN.md, etc.)

## Coding Tasks Only

`CODER_IMPLEMENTATION_SOP.md` defines execution discipline for **writing or editing code only**. Do not read it for documentation, review, analysis, planning, or validation tasks.

## Key Documents

- **README.md** — Master index (start here)
- **QWEN.md** — Comprehensive project reference
- **docs/developer/ARCHITECTURAL_REFACTOR.md** — Consolidated architectural refactor documentation
- **docs/developer/JOB_DEFINITION_DICTIONARY.md** — Job state model reference
- **docs/developer/CODER_IMPLEMENTATION_SOP.md** — Execution discipline (read before writing code)

## Archive

Archived root guidance under `docs/archive/root-guidance/` is historical only.
