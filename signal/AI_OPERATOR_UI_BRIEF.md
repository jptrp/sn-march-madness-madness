# AI Operator Brief - UI Plan for sn-march-madness-madness

**Date**: 2026-02-18
**Audience**: AI operator using Signal
**Objective**: Understand the repo quickly and propose a UI plan (design + execution).

---

## Repo Snapshot

**Core idea**
- A bracket personality test: "press button -> meme artifact -> postable"
- Not a prediction engine, just vibes + math

**Inputs**
- CLI parameters: `--seed`, `--count`, `--pool`, `--roast`, `--out`, `--force`

**Primary outputs**
- `output/share_card_<seed>.txt`
- `output/signal_report_<seed>.md`
- `output/pool_card.txt`
- `output/superlatives_card.txt`
- `output/duel_card.txt`
- `output/sharepack/POST.txt`
- `output/leaderboard.json`

---

## UI Goal

Create a simple UI that:
- Runs a single card and a pool mode
- Shows the generated artifacts clearly
- Makes "share" frictionless (copy/paste ready)

---

## Constraints

- Keep it minimal and fast
- Preserve the artifact-first workflow
- No claims of prediction or accuracy

---

## Suggested Plan (Operator)

1) **Discovery**
   - Run the demo command in README
   - Confirm output files and formats
   - Identify which artifacts are most important for UI

2) **UI Concept**
   - Propose 1-2 screens max
   - Single-seed view + pool mode view
   - Explicit "copy" affordances for the share pack

3) **Execution Plan**
   - Select stack (lightweight web UI or local GUI)
   - Map CLI -> UI actions
   - Define data flow from `output/` files

4) **Deliverables**
   - Wireframe
   - Minimal UI spec
   - Implementation plan (phases + risks)

---

## Optional Nice-to-Haves (Moved from README)

- Add 1 screenshot to the README later: paste one share card + pool card as code blocks.
- Add a `--post-only` flag to regenerate the Slack post from an existing run without re-simulating.
