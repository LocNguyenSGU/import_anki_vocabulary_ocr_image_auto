# Agent Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add AI-first project documentation so future agents can orient quickly, follow the right workflow, and avoid known Anki/import pitfalls.

**Architecture:** Add a focused `docs/agent/` knowledge set split by concern: overview, architecture, data contracts, workflows, and pitfalls. Add a local `AGENTS.md` that points agents to the AI-first docs instead of forcing them to infer project behavior from README and source.

**Tech Stack:** Markdown, existing Python CLI project structure, AnkiConnect workflow

---

### Task 1: Create Agent-Facing Doc Structure

**Files:**
- Create: `docs/agent/overview.md`
- Create: `docs/agent/architecture.md`
- Create: `docs/agent/data-contracts.md`
- Create: `docs/agent/workflows.md`
- Create: `docs/agent/pitfalls.md`

- [ ] Draft `overview.md` with project purpose, scope, reading order, and the fastest orientation path.
- [ ] Draft `architecture.md` with module boundaries and the end-to-end flow from input JSON to Anki notes.
- [ ] Draft `data-contracts.md` with the JSON/CSV/history/Anki note model contracts, including `EntryKey`.
- [ ] Draft `workflows.md` with the standard operating procedures for adding lessons, building, importing, and re-importing safely.
- [ ] Draft `pitfalls.md` with the duplicate-detection root cause, lesson numbering constraints, and history-vs-Anki caveats.

### Task 2: Add Agent Entry Point

**Files:**
- Create: `AGENTS.md`

- [ ] Add a short local `AGENTS.md` that points future agents to `docs/agent/` and tells them which files to read first.

### Task 3: Align Existing Docs

**Files:**
- Modify: `README.md`

- [ ] Add one short AI-oriented pointer in `README.md` so maintainers know where the agent docs live.

### Task 4: Verify Documentation Consistency

**Files:**
- Verify: `docs/agent/*.md`
- Verify: `AGENTS.md`
- Verify: `README.md`

- [ ] Check that filenames, commands, and field names match the current codebase.
- [ ] Verify that `EntryKey`, `history/runs.json`, `mamino-anki build`, and `mamino-anki import-anki` are documented consistently.
- [ ] Run a quick repo grep after writing docs to confirm references are valid and typo-free.
