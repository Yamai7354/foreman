# Workspace Assessment and Priority Plan

Date: March 5, 2026
Scope: Top-level projects in `/Users/yamai/ai`
Method: Repository structure scan, README/docs quality check, dependency/test/CI signal review (no full runtime test execution in this pass)

## Executive Summary

You are not stuck because of lack of ideas. You are overloaded by too many parallel codebases with uneven documentation quality and inconsistent project hygiene.

Main pattern:
- A few strong core projects are real and valuable (`Raphael`, `agent_ecosystem`, `network_observatory`, `portfolio`)
- Several projects are partially formed or under-documented (`agents`, `ditto`, `playground`, `speech`)
- Some directories are support/archive containers and should be treated that way (`_project_summaries_v3`, `Rikka_Mikazuki`, `data`, `dnd`)

## Project-by-Project Status

## 1) Core Projects (High leverage)

### `Raphael`
Status: Advanced and active. Strong architecture, CI workflows, significant code surface.
Needs work:
- Reduce backlog markers (`TODO/FIXME`) and convert into tracked issues
- Tighten module boundaries to keep complexity manageable
- Keep docs synchronized with current runtime entry points

### `agent_ecosystem`
Status: Large monorepo with serious potential, but complexity is high.
Needs work:
- Standardize package boundaries and ownership between `packages/` and `projects/`
- Add/strengthen CI for monorepo-level sanity checks
- Reduce duplicated or mirrored content where possible

### `network_observatory`
Status: Most product-ready project in the workspace (good README, docs, tests, migration structure).
Needs work:
- Add CI pipeline (tests + lint + basic security/static checks)
- Improve release/versioning discipline
- Add one-click local smoke script for first-time setup confidence

### `portfolio`
Status: Useful tooling base with CLI and CI, but messaging/content is partially generic.
Needs work:
- Keep portfolio website aligned with actual active projects
- Ensure docs are curated (not only generated)
- Use reports as decision-driving artifacts, not just logs

## 2) Mid-tier Projects (Need stabilization)

### `ditto`
Status: Broad concept with many components; README is still placeholder.
Needs work:
- Replace placeholder README with architecture + runbook
- Declare MVP boundaries (what is in scope now vs later)
- Add clear test strategy for API/core modules

### `agents`
Status: Utility/agent collection exists; project framing is missing.
Needs work:
- Replace placeholder README
- Define contract for adding/routing agents
- Add quick smoke tests around core routing modules

### `playground`
Status: Experiment sandbox; currently noisy and hard to navigate.
Needs work:
- Split active experiments from archived ones
- Add index README mapping each experiment to purpose/status
- Avoid promoting playground artifacts into production without gate criteria

### `speech`
Status: Appears asset-heavy with minimal engineering docs.
Needs work:
- Replace placeholder README
- Clarify whether this is data prep, synthesis tooling, or model project
- Add reproducible scripts for data processing workflow

## 3) Support/Archive Directories (Do not prioritize as products)

### `_project_summaries_v3`
Treat as generated/reference snapshots. Keep out of active roadmap except when using as source material.

### `Rikka_Mikazuki`, `data`, `dnd`
Treat as stubs or data containers unless you explicitly promote one into an active project.

## Skill Plan (What to Improve in You)

## Immediate Skills (next 30 days)

1. Project triage and scope control
- Pick one primary build project + one maintenance project at a time
- Write explicit “not now” lists to reduce cognitive load

2. Architecture communication
- Replace placeholder READMEs with 1-page architecture + runbook docs
- Keep one source of truth per project for entry points and commands

3. Test discipline
- For each active project: define smoke, unit, integration layers
- Require at least smoke tests before declaring a feature “done”

4. Delivery consistency
- Same command style across projects (`make`, or `just`, or `task`)
- Same CI baseline (lint + tests + formatting)

## Intermediate Skills (30-90 days)

1. Monorepo governance
- Ownership boundaries, dependency constraints, and package policies

2. Operational engineering
- Health checks, failure budgets, and release checklists for long-running agents

3. Product narrative
- Turn technical capability into crisp “problem -> approach -> outcome” storytelling in portfolio artifacts

## Project Priorities (Recommended Start Order)

## Week 1 (Stabilize)

1. `portfolio`
- Keep this assessment as the canonical roadmap artifact
- Align website project cards and priorities with reality

2. `agents` + `ditto` + `speech` + `playground`
- Replace placeholder READMEs
- Add minimal run commands and status labels (`active`, `experimental`, `archived`)

## Week 2-3 (Reliability)

1. `network_observatory`
- Add CI and release checklist
- Confirm tests run clean on fresh environment

2. `agent_ecosystem`
- Create package ownership map and enforce boundaries
- Add root-level contributor/developer runbook

## Week 4 (Scale cleanly)

1. `Raphael`
- Burn down TODO debt into tracked issues
- Review architecture docs against current code reality

## 90-Day Outcomes to Target

- All active projects have non-placeholder README + quickstart + architecture note
- All active projects have CI baseline
- Experiments are separated from products
- Portfolio tells one clear story: “multi-agent AI systems + ops discipline + developer tooling”

## Practical Rule to Reduce Overwhelm

Use this weekly filter:
- Build: one project
- Maintain: one project
- Archive: everything else for this week

Anything not in Build/Maintain is intentionally paused, not ignored.

